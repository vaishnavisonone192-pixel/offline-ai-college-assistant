import os
import re
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import (
    clear_messages,
    activity_items,
    claim_legacy_messages,
    create_user,
    get_user_by_email,
    get_connection,
    get_user_by_id,
    history_items,
    initialize_database,
    list_messages,
    migrate_legacy_documents,
    save_document,
    save_message,
    soft_delete_activity,
)
from llama_service import OllamaServiceError, generate_response
from pdf_processor import extract_text

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "offline-studyroom-local-secret")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
UPLOAD_FOLDER = Path(__file__).with_name("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
initialize_database()
existing_users = []
with get_connection() as connection:
    existing_users = connection.execute("SELECT id FROM users").fetchall()
if len(existing_users) == 1:
    legacy_files = []
    for legacy_path in UPLOAD_FOLDER.glob("*.pdf"):
        try:
            legacy_files.append((legacy_path.name, len(extract_text(legacy_path))))
        except Exception:
            continue
    migrate_legacy_documents(existing_users[0][0], legacy_files)


def current_user():
    user_id = session.get("user_id")
    return get_user_by_id(user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user():
            return jsonify({"error": "Please log in to continue."}), 401
        return view(*args, **kwargs)

    return wrapped_view


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/chat")
def chat():
    return render_template("index.html")


@app.get("/api/history")
@login_required
def history():
    user_id = session["user_id"]
    return jsonify({"messages": list_messages(user_id), "items": activity_items(user_id)})


@app.delete("/api/history")
@login_required
def delete_history():
    clear_messages(session["user_id"])
    return jsonify({"ok": True, "permanent_backend_record": True})


@app.delete("/api/history/<kind>/<int:item_id>")
@login_required
def delete_history_item(kind, item_id):
    if kind not in {"question", "document"}:
        return jsonify({"error": "Unknown history item."}), 400
    if not soft_delete_activity(session["user_id"], kind, item_id):
        return jsonify({"error": "History item was not found."}), 404
    return jsonify({"ok": True, "permanent_backend_record": True})


@app.post("/api/upload")
@login_required
def upload_pdf():
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"error": "Choose a PDF file first."}), 400
    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    filename = secure_filename(uploaded_file.filename)
    if not filename:
        return jsonify({"error": "That filename is not valid."}), 400
    user_folder = app.config["UPLOAD_FOLDER"] / str(session["user_id"])
    user_folder.mkdir(exist_ok=True)
    file_path = user_folder / filename
    uploaded_file.save(file_path)
    try:
        text = extract_text(file_path)
    except Exception as error:
        file_path.unlink(missing_ok=True)
        return jsonify({"error": f"Could not read this PDF: {error}"}), 400

    if not text.strip():
        file_path.unlink(missing_ok=True)
        return jsonify({"error": "This PDF does not contain extractable text."}), 400
    save_document(session["user_id"], filename, len(text))
    return jsonify({"filename": filename, "characters": len(text), "text": text[:16000]})


@app.post("/api/chat")
@login_required
def ask_question():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    document_text = str(data.get("document_text", "")).strip()
    document_name = str(data.get("document_name", "")).strip() or None
    if not question:
        return jsonify({"error": "Ask a question before sending."}), 400

    prompt = (
        "You are an offline college study assistant. Give a clear, accurate, "
        "well-structured answer. If a document is provided, ground the answer "
        "in it and say when the document does not contain enough information.\n\n"
        f"DOCUMENT:\n{document_text[:16000] or '[No document attached]'}\n\n"
        f"STUDENT QUESTION:\n{question}"
    )
    message_id = save_message(session["user_id"], "user", question, document_name)
    try:
        answer = generate_response(prompt)
    except OllamaServiceError as error:
        return jsonify({"error": str(error)}), 503
    save_message(session["user_id"], "assistant", answer, document_name)
    return jsonify({"answer": answer, "document_name": document_name, "message_id": message_id})


@app.get("/api/auth/me")
def auth_me():
    user = current_user()
    return jsonify({"authenticated": bool(user), "user": user})


@app.post("/api/auth/signup")
def signup():
    data = request.get_json(silent=True) or {}
    name = re.sub(r"\s+", " ", str(data.get("name", "")).strip())
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if len(name) < 2:
        return jsonify({"error": "Enter your full name."}), 400
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Your password must contain at least 8 characters."}), 400
    if get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409
    user_id = create_user(name, email, generate_password_hash(password))
    claim_legacy_messages(user_id)
    session.clear()
    session["user_id"] = user_id
    return jsonify({"user": get_user_by_id(user_id)}), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Email or password is incorrect."}), 401
    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"user": get_user_by_id(user["id"])})


@app.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=True)