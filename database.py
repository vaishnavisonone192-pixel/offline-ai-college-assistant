import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).with_name("chatbot.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                document_name TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                characters INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        columns = {row[1] for row in connection.execute("PRAGMA table_info(messages)")}
        if "user_id" not in columns:
            connection.execute("ALTER TABLE messages ADD COLUMN user_id INTEGER REFERENCES users(id)")
        if "deleted_at" not in columns:
            connection.execute("ALTER TABLE messages ADD COLUMN deleted_at TEXT")
        document_columns = {row[1] for row in connection.execute("PRAGMA table_info(documents)")}
        if "deleted_at" not in document_columns:
            connection.execute("ALTER TABLE documents ADD COLUMN deleted_at TEXT")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_messages_deleted_at ON messages(deleted_at)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)")
        connection.commit()


def create_user(name, email, password_hash):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        connection.commit()
        return cursor.lastrowid


def get_user_by_email(email):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def claim_legacy_messages(user_id):
    with get_connection() as connection:
        connection.execute(
            "UPDATE messages SET user_id = ? WHERE user_id IS NULL",
            (user_id,),
        )
        connection.commit()


def save_message(user_id, role, content, document_name=None):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO messages (user_id, role, content, document_name) VALUES (?, ?, ?, ?)",
            (user_id, role, content, document_name),
        )
        connection.commit()
        return cursor.lastrowid


def list_messages(user_id, limit=100):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, role, content, document_name, created_at
            FROM messages
            WHERE user_id = ? AND deleted_at IS NULL
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def history_items(user_id, limit=12):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, content, document_name, created_at
            FROM messages
            WHERE user_id = ? AND role = 'user' AND deleted_at IS NULL
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def save_document(user_id, filename, characters):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO documents (user_id, filename, characters) VALUES (?, ?, ?)",
            (user_id, filename, characters),
        )
        connection.commit()
        return cursor.lastrowid


def migrate_legacy_documents(user_id, filenames):
    with get_connection() as connection:
        for filename, characters in filenames:
            exists = connection.execute(
                "SELECT 1 FROM documents WHERE user_id = ? AND filename = ?",
                (user_id, filename),
            ).fetchone()
            if not exists:
                connection.execute(
                    "INSERT INTO documents (user_id, filename, characters) VALUES (?, ?, ?)",
                    (user_id, filename, characters),
                )
        connection.commit()


def activity_items(user_id, limit=18):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, 'question' AS kind, content AS title, document_name, created_at
            FROM messages
            WHERE user_id = ? AND role = 'user' AND deleted_at IS NULL
            UNION ALL
            SELECT id, 'document' AS kind, filename AS title, filename AS document_name, created_at
            FROM documents
            WHERE user_id = ? AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, user_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def soft_delete_activity(user_id, kind, item_id):
    with get_connection() as connection:
        if kind == "document":
            cursor = connection.execute(
                "UPDATE documents SET deleted_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ? AND deleted_at IS NULL",
                (item_id, user_id),
            )
        else:
            cursor = connection.execute(
                "UPDATE messages SET deleted_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ? AND role = 'user' AND deleted_at IS NULL",
                (item_id, user_id),
            )
            connection.execute(
                "UPDATE messages SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ? AND id = (SELECT MIN(id) FROM messages WHERE user_id = ? AND role = 'assistant' AND id > ? AND deleted_at IS NULL)",
                (user_id, user_id, item_id),
            )
        connection.commit()
    return cursor.rowcount > 0


def clear_messages(user_id):
    with get_connection() as connection:
        connection.execute("UPDATE messages SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ? AND deleted_at IS NULL", (user_id,))
        connection.execute("UPDATE documents SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ? AND deleted_at IS NULL", (user_id,))
        connection.commit()
