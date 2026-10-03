import os
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver


# --------------------------------
# Load environment variables
# --------------------------------

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

# For Streamlit Cloud
if not groq_api_key:
    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        st.error("GROQ_API_KEY is not configured.")
        st.stop()


# --------------------------------
# Page configuration
# --------------------------------

st.set_page_config(
    page_title="AI Agent Chatbot",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------
# Title
# --------------------------------

st.title("🤖 AI Agent Chatbot")
st.caption("Powered by Groq + LangChain + LangGraph")


# --------------------------------
# Create LLM
# --------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=groq_api_key
)


# --------------------------------
# Memory
# --------------------------------

memory = InMemorySaver()


# --------------------------------
# Create Agent
# --------------------------------

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
    You are a helpful AI assistant.
    Remember the conversation history and use it
    when answering follow-up questions.
    """,
    checkpointer=memory
)


# --------------------------------
# Conversation ID
# --------------------------------

config = {
    "configurable": {
        "thread_id": "streamlit-user-1"
    }
}


# --------------------------------
# Chat history
# --------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------
# Sidebar
# --------------------------------

with st.sidebar:

    st.header("⚙️ Dashboard")

    st.write("### Model")
    st.write("Groq - GPT OSS 20B")

    st.write("### Features")
    st.write("✅ AI Chat")
    st.write("✅ Conversation Memory")
    st.write("✅ LangChain Agent")
    st.write("✅ LangGraph")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# --------------------------------
# Display previous messages
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------
# Chat input
# --------------------------------

question = st.chat_input("Ask me anything...")


if question:

    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)


    # AI response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = agent.invoke(
                {
                    "messages": [
                        ("user", question)
                    ]
                },
                config=config
            )

            answer = response["messages"][-1].content

            st.markdown(answer)


    # Save response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })