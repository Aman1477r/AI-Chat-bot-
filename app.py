import os
import sqlite3
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
)

from dotenv import load_dotenv
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_tavily import TavilySearch
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)


# ============================================================
# ENVIRONMENT AND PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

DB_PATH = BASE_DIR / "chat_memory.db"
VECTOR_DB_PATH = BASE_DIR / "vector_db"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from your .env file.")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing from your .env file.")

if not FLASK_SECRET_KEY:
    raise ValueError("FLASK_SECRET_KEY is missing from your .env file.")


# ============================================================
# FLASK AND LOGIN CONFIGURATION
# ============================================================

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Return JSON for unauthenticated chat requests.
# Redirect ordinary browser requests to the login page.
@login_manager.unauthorized_handler
def unauthorized():
    if request.path == "/chat":
        return jsonify({
            "error": "Please log in to use the chatbot."
        }), 401

    return redirect(url_for("login"))


# ============================================================
# DATABASE
# ============================================================

def initialize_database():
    with sqlite3.connect(DB_PATH, timeout=30) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_thread_id
            ON chat_messages(thread_id, id)
        """)

        conn.commit()


# Create the tables if they don't already exist.
initialize_database()


# ============================================================
# USER MODEL
# ============================================================

class User(UserMixin):

    def __init__(self, user_id, username):
        self.id = str(user_id)
        self.username = username


@login_manager.user_loader
def load_user(user_id):

    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT id, username FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return User(row["id"], row["username"])


# ============================================================
# CONVERSATION MEMORY
# ============================================================

def get_history(thread_id, limit=20):
    """Load recent messages for one user's conversation."""

    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM chat_messages
            WHERE thread_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (thread_id, limit),
        ).fetchall()

    # Put the messages in chronological order.
    rows.reverse()

    messages = []

    for role, content in rows:
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    return messages


def save_message(thread_id, role, content):
    """Save a user or assistant message in SQLite."""

    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (thread_id, role, content)
            VALUES (?, ?, ?)
            """,
            (thread_id, role, content),
        )

        conn.commit()


# ============================================================
# LANGUAGE MODEL
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=GROQ_API_KEY,
)


# ============================================================
# WEB SEARCH
# ============================================================

web_search = TavilySearch(
    max_results=5,
    topic="general",
)


# ============================================================
# PDF RAG
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

if not VECTOR_DB_PATH.exists():
    raise FileNotFoundError(
        f"Vector database not found: {VECTOR_DB_PATH}. "
        "Run rag.py first to create it."
    )

vector_db = Chroma(
    persist_directory=str(VECTOR_DB_PATH),
    embedding_function=embeddings,
)

retriever = vector_db.as_retriever(
    search_kwargs={"k": 4}
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a helpful AI assistant that answers in simple, natural language.

RESPONSE FORMATTING RULES:
- Answer in a clear, conversational, line-by-line format.
- Use simple English and short sentences.
- Avoid tables unless the user explicitly asks for a table.
- Do not use numbered lists for ordinary explanations unless useful.
- Use short headings and bullet points when they improve readability.
- Put each main point on a separate line.
- Explain technical terms in simple words.
- Avoid overly long paragraphs.
- Answer the user's exact question directly.
- For news, give each headline on a separate line with a brief explanation.
- Include sources or links for web search claims when available.
- Never invent sources, links, or facts.

MEMORY:
- Use the supplied conversation history for follow-up questions.
- Remember relevant facts from previous messages.
- Do not invent personal information.

PDF DOCUMENTS:
- Use the supplied PDF context when relevant.
- If the PDF does not contain the answer, say so honestly.

WEB SEARCH:
-WEB SEARCH AND SOURCES:
- Use supplied web search results for current information.
- When web search results include URLs, preserve the original URLs.
- If the user asks for a source, link, reference, or citation, provide the relevant source URLs as clickable Markdown links.
- Format links like: [Source title](https://example.com/article).
- Include the source title and a short explanation of what it supports.
- Never invent URLs, titles, or sources.
- If no source URLs are available, clearly say that the links were not provided in the search results.
- When answering a current-news question, include a "Sources" section with relevant links whenever URLs are available.
- Keep the answer simple and line by line.
GENERAL:
- Be helpful, accurate, and friendly.
- Prefer simple explanations suitable for a beginner.
- Use examples when they help understanding.
"""

# ============================================================
# SIGNUP
# ============================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3 or len(username) > 40:
            flash("Username must be between 3 and 40 characters.")
            return redirect(url_for("signup"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("signup"))

        password_hash = generate_password_hash(password)

        try:
            with sqlite3.connect(DB_PATH, timeout=30) as conn:
                conn.execute(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?)
                    """,
                    (username, password_hash),
                )

                conn.commit()

        except sqlite3.IntegrityError:
            flash("That username already exists. Please choose another.")
            return redirect(url_for("signup"))

        flash("Account created successfully. Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.row_factory = sqlite3.Row

            user_row = conn.execute(
                """
                SELECT id, username, password_hash
                FROM users
                WHERE username = ?
                """,
                (username,),
            ).fetchone()

        if user_row and check_password_hash(
            user_row["password_hash"],
            password,
        ):
            user = User(
                user_row["id"],
                user_row["username"],
            )

            login_user(user)

            # The same account gets the same conversation ID
            # when logging in from another browser.
            session["thread_id"] = f"user-{user.id}"

            return redirect(url_for("home"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()
    session.clear()

    flash("You have been logged out.")
    return redirect(url_for("login"))


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
@login_required
def home():
    return render_template("index.html")


# ============================================================
# CHAT API
# ============================================================

@app.route("/chat", methods=["POST"])
@login_required
def chat():

    try:
        data = request.get_json(silent=True) or {}

        question = str(data.get("message", "")).strip()

        if not question:
            return jsonify({
                "error": "Please enter a message."
            }), 400

        # Each account has its own conversation history.
        # This ID remains the same across browsers for that account.
        thread_id = f"user-{current_user.id}"

        # Load history before saving the new question.
        history = get_history(thread_id, limit=20)

        # Retrieve relevant PDF passages.
        documents = retriever.invoke(question)

        if documents:
            pdf_context = "\n\n".join(
                doc.page_content for doc in documents
            )
        else:
            pdf_context = "No relevant PDF passages were retrieved."

        user_prompt = f"""
PDF CONTEXT:
--------------------
{pdf_context}
--------------------

CURRENT QUESTION:
{question}

Use the conversation history when relevant.
Use the PDF context when relevant.
Use web search results when available and relevant.
Do not invent facts.
"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *history,
            HumanMessage(content=user_prompt),
        ]

        # Save the original question.
        save_message(thread_id, "user", question)

        # Generate the initial response.
        response = llm.invoke(messages)
        answer = response.content

        if isinstance(answer, list):
            answer = "\n".join(
                block.get("text", "")
                for block in answer
                if isinstance(block, dict)
            )

        answer = str(answer).strip()

        # Search the web for questions that likely need current data.
        latest_keywords = (
            "latest",
            "current",
            "recent",
            "today",
            "news",
            "this week",
            "right now",
            "updates",
        )

        needs_web_search = any(
            keyword in question.lower()
            for keyword in latest_keywords
        )

        if needs_web_search:

            try:
                search_results = web_search.invoke({
                    "query": question
                })

                follow_up_messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    *history,
                    HumanMessage(content=f"""
User question:
{question}

Web search results:
{search_results}

Relevant PDF context:
{pdf_context}

Answer clearly using the web search results where relevant.
Do not invent facts.
"""),
                ]

                web_response = llm.invoke(follow_up_messages)
                web_answer = web_response.content

                if isinstance(web_answer, list):
                    web_answer = "\n".join(
                        block.get("text", "")
                        for block in web_answer
                        if isinstance(block, dict)
                    )

                if isinstance(web_answer, str) and web_answer.strip():
                    answer = web_answer.strip()

            except Exception as search_error:
                app.logger.warning(
                    "Web search failed: %s",
                    search_error,
                )

                # Keep the original answer if web search fails.

        # Save the final answer for future conversations.
        save_message(thread_id, "assistant", answer)

        return jsonify({
            "answer": answer
        })

    except Exception:
        app.logger.exception("Chat request failed")

        return jsonify({
            "error": (
                "The chatbot encountered an error. "
                "Check the Flask terminal for details."
            )
        }), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
    )