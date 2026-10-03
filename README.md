# 🤖 AI Chatbot

An AI-powered chatbot built with **Python, Flask, LangChain, LangGraph, and Groq**.

The chatbot can answer questions, maintain conversation context, and provide fast AI-generated responses through a simple and modern web interface.

## 🌐 Live Demo

🚀 **Try the AI Chatbot:**  
https://ai-chat-bot-rvxg.onrender.com/

## 📂 GitHub Repository

🔗 **Source Code:**  
https://github.com/Aman1477r/AI-Chat-bot-

---

## ✨ Features

- 💬 AI-powered chat
- 🧠 Conversation memory
- ⚡ Fast AI responses
- 🤖 GPT-OSS 20B model
- 🔗 LangChain integration
- 🕸️ LangGraph agent
- 🎨 Modern and responsive user interface
- 📊 Dashboard
- ⚙️ Settings page
- 🌙 Dark/Light mode
- 📱 Responsive design
- 🚀 Deployed online using Render

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| 🐍 Python | Main programming language |
| 🌐 Flask | Web application framework |
| 🔗 LangChain | AI/LLM application framework |
| 🕸️ LangGraph | Agent and conversation workflow |
| ⚡ Groq | AI model API |
| 🤖 GPT-OSS 20B | Language model |
| 🎨 HTML | Web page structure |
| 🎨 CSS | Styling and animations |
| ⚙️ JavaScript | Frontend interaction |
| 🚀 Render | Cloud deployment |
| 🐙 GitHub | Source code and version control |

---

## 🧠 How It Works

The basic flow of the chatbot is:

```text
User
  ↓
Web Interface
  ↓
Flask Backend
  ↓
LangChain
  ↓
LangGraph
  ↓
Groq API
  ↓
GPT-OSS 20B
  ↓
AI Response
  ↓
Web Interface
```

The user sends a message through the website.

Flask receives the message and sends it to the AI agent.

LangChain and LangGraph manage the AI workflow and conversation context.

Groq processes the request using the GPT-OSS 20B model.

The generated response is then returned to the user.

---

## 📁 Project Structure

```text
AI-Chat-bot-
│
├── app.py
│
├── requirements.txt
│
├── .gitignore
│
├── notebooks/
│   └── Langchain.ipynb
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
```

### File Description

**`app.py`**  
Main Flask application and AI chatbot backend.

**`templates/index.html`**  
Main webpage and chatbot interface.

**`static/style.css`**  
Website styling, animations, dashboard design, and responsive layout.

**`static/script.js`**  
Handles chat messages, page navigation, theme switching, and frontend interactions.

**`notebooks/`**  
Contains notebooks used during development and experimentation.

**`requirements.txt`**  
Contains the Python packages required to run the project.

---

# 🚀 Run the Project Locally

If you want to run this project on your computer, follow these steps.

## 1. Clone the repository

```bash
git clone https://github.com/Aman1477r/AI-Chat-bot-.git
```

Move into the project:

```bash
cd AI-Chat-bot-
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv env
```

Activate it:

```bash
env\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Add your API key

Create a file named:

```text
.env
```

Add your Groq API key:

```text
GROQ_API_KEY=your_groq_api_key_here
```

⚠️ **Never upload your `.env` file to GitHub.**

The `.gitignore` file is used to prevent secret files from being uploaded.

---

## 5. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Your chatbot should now be running locally.

---

# ☁️ Deployment

This project is deployed using **Render**.

The application is connected to the GitHub repository and runs as a Flask web service.

### Deployment Configuration

```text
Build Command:
pip install -r requirements.txt
```

```text
Start Command:
gunicorn app:app
```

The Groq API key is stored securely as an environment variable on the deployment platform.

---

# 🔐 Security

API keys and other sensitive information should never be committed to GitHub.

This project uses:

```text
.env
```

for local environment variables.

The `.gitignore` file prevents sensitive files from being uploaded.

Example:

```text
.env
env/
__pycache__/
*.pyc
```

---

# 🎯 Project Goal

The main goal of this project is to understand how modern AI applications are built and deployed.

Through this project, I worked with:

- Large Language Models
- AI APIs
- LangChain
- LangGraph
- Flask
- Frontend development
- Conversation memory
- Git and GitHub
- Cloud deployment

---

# 📚 What I Learned

While building this project, I learned how to:

- Connect an LLM to a Python application
- Use LangChain for AI application development
- Build an agent using LangGraph
- Create a Flask backend
- Connect frontend and backend using APIs
- Manage environment variables
- Use Git and GitHub
- Deploy a Python application on Render
- Build a responsive and interactive web interface

---

# 🔮 Future Improvements

Some features that can be added in future versions:

- 👤 User authentication
- 💾 Database-based conversation history
- 📄 PDF and document Q&A
- 🔍 Web search
- 🧠 RAG (Retrieval-Augmented Generation)
- 🛠️ AI tools and function calling
- 🗂️ Multiple conversations
- 🗑️ Clear conversation option
- 📊 Advanced analytics
- 🎙️ Voice input and output

---

# 👨‍💻 Developer

**Aman**

🎓 Computer Science / AI Student

Interested in:

- Generative AI
- Machine Learning
- Python
- LangChain
- AI Agents
- Full-Stack AI Applications

---

## ⭐ Support

If you find this project interesting, feel free to ⭐ the repository!

### 🚀 Try the Project

**Live Demo:**  
https://ai-chat-bot-rvxg.onrender.com/

**Source Code:**  
https://github.com/Aman1477r/AI-Chat-bot-

---

## 📄 License

This project is created for learning, educational, and portfolio purposes.
