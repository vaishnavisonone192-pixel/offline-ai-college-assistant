# Offline AI College Assistant

A private college study assistant powered by Flask, SQLite, PyMuPDF, and a local Ollama model. Questions, uploaded PDFs, and chat history stay on this computer.

## Run locally

1. Install [Ollama](https://ollama.com/) for Windows and start the Ollama application.
2. Download the model once:

```powershell
ollama pull llama3.2:3b
```

3. Create and activate the Python environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Start the web app:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Ollama must be running locally at `http://127.0.0.1:11434`.

## Accounts and history

The application includes local account creation and login. Create an account from the first screen using an email address and a password with at least 8 characters. Passwords are stored as secure hashes, not plain text.

Each account has its own chat history. The Recent history panel shows that user's previous questions, and the SQLite `messages.user_id` column keeps users' conversations separated. PDFs uploaded after login are stored under `uploads/<user_id>/`.

Uploaded PDFs are also recorded in the `documents` table, so the Recent history panel shows both questions and PDF activity. The list refreshes immediately after a question or upload-related action.

## History deletion

Each Recent history item has a delete icon. Deleting an item removes it from the active UI history, but does not destroy the backend record. SQLite stores the original message or document with a `deleted_at` timestamp for permanent retention. The top clear-history control applies the same archive behavior to all active history for the account.

The existing messages created before accounts were added are automatically assigned to the first account created, preserving the original local study history. The existing PDF files in `uploads/` are not deleted during migration.

For local development, the default session secret is built in. Set a private value before sharing the application beyond your own computer:

```powershell
$env:SECRET_KEY = "replace-this-with-a-long-random-local-secret"
python app.py
```

## Configuration

The defaults are `llama3.2:3b` and `http://127.0.0.1:11434`. To use another local Ollama model or endpoint:

```powershell
$env:OLLAMA_MODEL = "llama3.2:3b"
$env:OLLAMA_URL = "http://127.0.0.1:11434"
python app.py
```

PDF uploads are limited to 16 MB. Extracted text is used as context for the next question and is not sent to any cloud service.
