import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not configured.")

app = Flask(__name__)

# -----------------------------
# AI MODEL
# -----------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=groq_api_key
)

memory = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
    You are a helpful AI assistant.

    Give clear, accurate and friendly answers.

    Explain difficult topics in simple language.

    Help users with:
    - Programming
    - Python
    - AI
    - Machine Learning
    - Generative AI
    - College studies
    - General questions

    Remember the conversation history and use it
    when answering follow-up questions.
    """,
    checkpointer=memory
)


# -----------------------------
# MAIN PAGE
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# CHAT API
# -----------------------------

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        question = data.get("message", "").strip()

        if not question:

            return jsonify({
                "error": "Please enter a message."
            }), 400

        config = {
            "configurable": {
                "thread_id": "user-1"
            }
        }

        response = agent.invoke(
            {
                "messages": [
                    ("user", question)
                ]
            },
            config=config
        )

        answer = response["messages"][-1].content

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )