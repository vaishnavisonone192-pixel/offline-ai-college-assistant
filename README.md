# 🎓 Offline AI College Assistant

<p align="center">

**A private, local, and intelligent college study assistant powered by Llama 3.2 3B and Ollama.**

Ask questions, chat with your local AI, upload study PDFs, and maintain personal chat history — **without sending your data to cloud AI services.**

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge\&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge\&logo=flask)
![Llama](https://img.shields.io/badge/Llama-3.2%203B-purple?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-white?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge\&logo=sqlite)
![PyMuPDF](https://img.shields.io/badge/PDF-PyMuPDF-red?style=for-the-badge)

</p>

---

## 🌟 Project Overview

**Offline AI College Assistant** is a locally hosted AI-powered study assistant designed for college students.

The application uses **Llama 3.2 3B**, running locally through **Ollama**, to answer questions and assist with study-related tasks.

Unlike cloud-based AI applications, the core AI processing happens directly on the user's computer.

### 💡 What makes this project different?

> **Your questions stay local. Your documents stay local. Your chat history stays local.**

The system is designed to provide an AI-powered learning environment while reducing dependence on external cloud AI services.

---

## ✨ Key Features

| Feature                   | Description                                                 |
| ------------------------- | ----------------------------------------------------------- |
| 🤖 Local AI Chat          | Chat with Llama 3.2 3B locally                              |
| 🔒 Privacy First          | Questions and documents remain on the local machine         |
| 📚 Study Assistant        | Ask questions about programming, AI, ML and academic topics |
| 📄 PDF Upload             | Upload study materials and PDF notes                        |
| 🔎 PDF Question Answering | Ask questions using uploaded document content               |
| 👤 Local Accounts         | Create and manage local user accounts                       |
| 💬 Chat History           | Store previous conversations                                |
| 🗑️ History Management    | Delete/archive individual or complete history               |
| 🗃️ SQLite Database       | Store accounts, messages and document information           |
| 🌐 Web Interface          | Access the assistant through a browser                      |
| ⚡ Local Processing        | No cloud AI API is required during normal operation         |
| ⚙️ Configurable Model     | Change the Ollama model through environment variables       |

---

# 🧠 How It Works

The application follows this architecture:

```text
                    👩‍🎓 STUDENT
                         │
                         ▼
              ┌─────────────────────┐
              │   Web Interface     │
              │   HTML / CSS / JS   │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │       Flask         │
              │    Python Backend   │
              └───────┬─────┬───────┘
                      │     │
             ┌────────┘     └──────────┐
             ▼                         ▼
      ┌─────────────┐           ┌──────────────┐
      │   SQLite    │           │ PDF Processor│
      │   Database  │           │   PyMuPDF    │
      └─────────────┘           └───────┬──────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │ Extracted Text│
                                └───────┬───────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │      Ollama      │
                              │                  │
                              │   Llama 3.2 3B   │
                              └────────┬─────────┘
                                       │
                                       ▼
                              🤖 AI Generated Answer
```

---

# 🔄 AI Question Flow

When a student asks a normal question:

```text
Student Question
       ↓
Flask Application
       ↓
Ollama Local API
       ↓
Llama 3.2 3B
       ↓
AI Response
       ↓
SQLite Chat History
       ↓
Student
```

The model runs locally through Ollama.

---

# 📄 PDF Question Answering

The application can also work with uploaded study materials.

```text
              📄 PDF
                │
                ▼
          PyMuPDF Parser
                │
                ▼
          Extracted Text
                │
                ▼
       Relevant Document Context
                │
                ▼
          Llama 3.2 3B
                │
                ▼
          🤖 AI Answer
```

For example:

**Student uploads:**

```text
Machine_Learning_Notes.pdf
```

Then asks:

```text
What is supervised learning?
```

The application extracts relevant text from the document and uses it as context for generating the answer.

---

# 🔐 Privacy & Offline Design

Privacy is one of the main goals of this project.

The application is designed so that:

* 🔒 Chat messages remain on the local computer.
* 📄 Uploaded PDFs remain on the local computer.
* 🗃️ Chat history is stored in local SQLite.
* 🤖 Llama runs through local Ollama.
* 🌐 No external cloud AI API is required for normal operation.
* 🔑 User passwords are stored using secure password hashes rather than plain text.

### Internet requirement

Internet access is required initially to:

1. Download Ollama.
2. Download the Llama model.
3. Install Python dependencies.

After setup, the application can be operated locally without requiring cloud AI services.

---

# 👤 User Accounts

The application supports local account creation and login.

Users can create an account using:

* Email address
* Password

Passwords must contain at least **8 characters**.

Each account has its own conversation history.

The database associates messages with the corresponding user through:

```text
messages.user_id
```

Uploaded documents are organized by user:

```text
uploads/
│
├── user_1/
│   ├── notes.pdf
│   └── machine_learning.pdf
│
└── user_2/
    └── python_notes.pdf
```

---

# 💬 Chat History

The Recent History panel displays previous activity.

It can contain:

* 💬 Questions
* 🤖 AI responses
* 📄 PDF activity
* 🕒 Previous conversations

Each history item can be deleted from the active interface.

The application uses a soft-delete/archive approach rather than immediately destroying the backend record.

Deleted records receive a:

```text
deleted_at
```

timestamp.

This provides better data management while keeping the active interface clean.

---

# 🗃️ Database

The application uses **SQLite** because it is lightweight and works well for a local desktop-style application.

The database stores information such as:

```text
Users
├── id
├── email
├── password_hash
└── created_at

Messages
├── id
├── user_id
├── user_message
├── ai_response
├── timestamp
└── deleted_at

Documents
├── id
├── user_id
├── filename
├── uploaded_at
└── deleted_at
```

---

# 🛠️ Technology Stack

### Backend

* 🐍 Python
* 🌐 Flask
* 🗃️ SQLite

### Artificial Intelligence

* 🦙 Llama 3.2 3B
* 🦙 Ollama

### Document Processing

* 📄 PyMuPDF

### Frontend

* HTML5
* CSS3
* JavaScript

### Development Environment

* Windows 11
* Python virtual environment
* Local Ollama server

---

# 📁 Project Structure

```text
offline-ai-college-assistant/
│
├── app.py
├── database.py
├── llama_service.py
├── pdf_processor.py
│
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── index.html
│   └── chat.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── uploads/
│   └── <user_id>/
│
└── database/
    └── chatbot.db
```

> ⚠️ The `venv/`, database files containing personal data, uploaded PDFs, `.env` files, passwords, API keys, and model files should not be committed to GitHub.

---

# ⚙️ Requirements

Before running the project, install:

### Software

* Windows 10/11
* Python 3.x
* Ollama
* Git

### AI Model

```powershell
ollama pull llama3.2:3b
```

### Python packages

```text
Flask
Ollama
PyMuPDF
```

---

# 🚀 Installation

## 1️⃣ Clone the repository

```powershell
git clone https://github.com/YOUR-USERNAME/offline-ai-college-assistant.git
```

Move into the project:

```powershell
cd offline-ai-college-assistant
```

---

## 2️⃣ Create a virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3️⃣ Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 4️⃣ Install and start Ollama

Install Ollama for Windows.

Then download Llama 3.2 3B:

```powershell
ollama pull llama3.2:3b
```

Verify the model:

```powershell
ollama list
```

You should see:

```text
llama3.2:3b
```

---

## 5️⃣ Start the application

```powershell
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

Ollama should be available locally at:

```text
http://127.0.0.1:11434
```

---

# 🔧 Configuration

The default configuration is:

```text
Model:
llama3.2:3b

Ollama URL:
http://127.0.0.1:11434
```

You can change the model:

```powershell
$env:OLLAMA_MODEL = "llama3.2:3b"
```

You can also change the Ollama endpoint:

```powershell
$env:OLLAMA_URL = "http://127.0.0.1:11434"
```

For local development, a default session secret is provided.

Before sharing the application beyond your own computer, set a private secret:

```powershell
$env:SECRET_KEY = "replace-this-with-a-long-random-local-secret"
```

Then start the application:

```powershell
python app.py
```

---

# 📏 PDF Upload Limit

PDF uploads are limited to:

```text
16 MB
```

Extracted PDF text is processed locally and used as context for the next question.

---

# 🧪 Testing

The project can be tested using the following scenarios:

| Test Case           | Expected Result                         |
| ------------------- | --------------------------------------- |
| Create account      | Account created successfully            |
| Login               | User successfully authenticated         |
| Ask AI question     | Llama generates response                |
| Upload PDF          | PDF stored locally                      |
| Ask PDF question    | Answer generated using document context |
| View history        | Previous activity displayed             |
| Delete history item | Item removed from active history        |
| Clear history       | Active history archived                 |
| Disable internet    | Local AI continues to work              |

---

# 📊 Performance Evaluation

The project can be evaluated using:

* Response time
* Model loading time
* Number of questions answered
* PDF processing time
* Memory usage
* Offline functionality
* Answer quality

Example evaluation:

```text
Model: Llama 3.2 3B
Runtime: Ollama
Hardware: Intel Core i5 + 16 GB RAM
Environment: Windows 11
```

Performance may vary depending on the computer, prompt length, document size, and system load.

---

# 🎯 Project Objectives

The main objectives of this project are:

1. To develop a locally hosted AI study assistant.
2. To integrate Llama 3.2 3B using Ollama.
3. To provide an interactive web interface.
4. To support local user accounts.
5. To maintain individual chat histories.
6. To process educational PDF documents.
7. To provide document-based question answering.
8. To store application data using SQLite.
9. To minimize dependency on cloud AI services.
10. To demonstrate practical use of local Large Language Models.

---

# 🎓 Use Cases

The Offline AI College Assistant can help students with:

### 📚 Academic Learning

```text
Explain object-oriented programming.
```

### 🐍 Programming

```text
Explain Python inheritance with an example.
```

### 🤖 Artificial Intelligence

```text
What is supervised learning?
```

### 📄 Study Notes

Upload a PDF and ask:

```text
Summarize chapter 2.
```

### 🔍 Document Questions

```text
What are the advantages mentioned in this document?
```

---

# 🌱 Future Enhancements

Future versions could include:

* 🎤 Voice input
* 🔊 AI voice responses
* 🧠 Embedding-based semantic search
* 📚 Multiple document collections
* 🔎 Advanced RAG pipeline
* 📱 Mobile application
* 👥 Multi-user administration
* 📊 Student analytics dashboard
* 🌍 Multilingual support
* 📝 Automatic quiz generation
* 🎯 Personalized study plans
* 📑 Automatic notes generation
* 🧪 Automated evaluation of AI responses

---

# 🏆 Why This Project?

Traditional college applications often require students to search through multiple sources to find answers.

This project combines:

```text
              AI
               +
          Local Processing
               +
           Documents
               +
          Chat History
               +
          Web Interface
               =
      🎓 Smart Study Assistant
```

The project demonstrates practical implementation of:

* Artificial Intelligence
* Large Language Models
* Natural Language Processing
* Web Development
* Database Management
* Document Processing
* Local AI Deployment

---

# 📸 Screenshots

Add screenshots of your application here as the project develops.

### 🏠 Login / Home Screen

```text
screenshots/login.png
```

### 💬 AI Chat

```text
screenshots/chat.png
```

### 📄 PDF Upload

```text
screenshots/pdf-upload.png
```

### 📚 Document Question Answering

```text
screenshots/pdf-chat.png
```

### 🗃️ Chat History

```text
screenshots/history.png
```

> 💡 A short GIF showing the user asking a question and receiving an AI response would make the GitHub repository much more attractive.

---

# 🎥 Demo

Add a short screen recording or GIF demonstrating:

```text
Login
  ↓
Ask Question
  ↓
Llama Generates Answer
  ↓
Upload PDF
  ↓
Ask PDF Question
  ↓
View Chat History
```

Example:

```text
demo/
└── offline-ai-demo.gif
```

---

# 🔒 Security Notes

This project is designed primarily for **local academic and development use**.

Before deploying beyond your personal computer:

* Change the default `SECRET_KEY`.
* Never commit passwords.
* Never commit `.env` files.
* Never commit API keys.
* Validate uploaded files.
* Restrict upload sizes.
* Use secure production configuration.
* Review authentication and authorization settings.

---

# ⚠️ Limitations

Llama 3.2 3B is a relatively small local language model.

Therefore:

* Responses may not always be factually correct.
* Complex reasoning may be weaker than larger models.
* Response speed depends on available CPU/RAM.
* PDF answers depend on the quality of extracted text.
* The system is primarily designed for local educational use.

AI-generated answers should therefore be verified for important academic or factual information.

---

# 📜 License

Add the license that matches your project's intended distribution and the licenses of the components/models you use.

If this repository is primarily for a college project, you can also include a project-specific academic notice here.

---

# 👩‍💻 Author

**Vaishnavi**

Final Year College Project

**Project:** Offline AI College Assistant
**Technology:** Llama 3.2 3B + Ollama + Python + Flask + SQLite

---

<p align="center">

### 🤖 Powered by Local AI

**Llama 3.2 3B • Ollama • Python • Flask • SQLite**

### 🔒 Private • 📚 Educational • ⚡ Local • 🧠 Intelligent

</p>
