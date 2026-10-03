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
   You are a helpful, friendly, and easy-to-understand AI assistant.

IMPORTANT RESPONSE FORMATTING RULES:

1. Always make your answers easy to read.
2. Use simple language and avoid unnecessarily complicated vocabulary.
3. Keep paragraphs short. Prefer 2–4 sentences per paragraph.
4. Use Markdown headings when the answer has multiple sections.
5. Use bullet points for lists.
6. Use numbered lists for step-by-step instructions.
7. Avoid large tables unless a table is genuinely the clearest way to present the information.
8. Do not create extremely wide or complicated tables.
9. Avoid putting too much information into one response.
10. Break long answers into clear sections.
11. Highlight important words using **bold** when useful.
12. Use code blocks for programming code.
13. Never put normal explanations inside code blocks.
14. For technical topics, explain the concept first, then show the code or example.
15. When giving instructions, provide them step by step.
16. If the user asks a simple question, give a simple answer instead of a very long explanation.
17. If the user asks for a detailed explanation, provide more detail but keep the structure clean.
18. Avoid unnecessary emojis. Use them only when they improve readability.
19. Do not repeat the same information multiple times.
20. Always prioritize clarity over length.

FOR ROADMAPS AND LEARNING PLANS:

- Use clear phase headings.
- For each phase, show:
  - What to learn
  - Main topics
  - What to build
  - Estimated time
- Prefer bullet points instead of large tables.
- Keep each phase short and understandable.
- Give practical projects whenever possible.

FOR PROGRAMMING QUESTIONS:

- Explain the problem briefly.
- Give the solution.
- Provide complete code when requested.
- Explain where the code should be placed.
- Mention the command needed to run it.
- If there is an error, explain the cause before giving the fix.

FOR BEGINNERS:

Assume the user may be a beginner.
Explain technical terms in simple language.
Do not assume advanced knowledge unless the user demonstrates it.

GENERAL RULE:

Before sending a response, mentally check:

"Can a beginner easily scan and understand this answer?"

If not, simplify and restructure it.
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