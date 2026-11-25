
import sqlite3
from pathlib import Path
from datetime import datetime


# -----------------------------------
# DATABASE CONFIGURATION
# -----------------------------------

DB_PATH = Path(__file__).resolve().parent / "assistant.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# -----------------------------------
# DATABASE INITIALIZATION
# -----------------------------------

def init_db():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature TEXT NOT NULL,
            user_input TEXT NOT NULL,
            response TEXT NOT NULL,
            feedback TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            feedback TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (chat_id)
            REFERENCES chat_sessions(id)
            ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY
        )
    """)

    connection.commit()

    # -----------------------------------
    # MIGRATE OLD CONVERSATIONS
    # -----------------------------------

    cursor.execute("""
        SELECT version
        FROM schema_migrations
        WHERE version = ?
    """, ("legacy_conversations_migrated",))

    migration_done = cursor.fetchone()

    if not migration_done:

        cursor.execute("""
            SELECT id, feature, user_input, response,
                   feedback, created_at
            FROM conversations
            ORDER BY id
        """)

        old_records = cursor.fetchall()

        for record in old_records:

            (
                old_id,
                feature,
                user_input,
                response,
                feedback,
                created_at
            ) = record

            title = str(user_input).replace("\n", " ").strip()

            if len(title) > 35:
                title = title[:35].rsplit(" ", 1)[0] + "..."

            if not title:
                title = feature

            cursor.execute("""
                INSERT INTO chat_sessions
                (title, created_at, updated_at)
                VALUES (?, ?, ?)
            """, (title, created_at, created_at))

            chat_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO chat_messages
                (chat_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
            """, (chat_id, "user", user_input, created_at))

            cursor.execute("""
                INSERT INTO chat_messages
                (chat_id, role, content, feedback, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                chat_id,
                "assistant",
                response,
                feedback,
                created_at
            ))

        cursor.execute("""
            INSERT INTO schema_migrations (version)
            VALUES (?)
        """, ("legacy_conversations_migrated",))

    connection.commit()
    connection.close()


# -----------------------------------
# CREATE NEW CHAT
# -----------------------------------

def create_chat(title="New Chat"):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO chat_sessions
        (title, created_at, updated_at)
        VALUES (?, ?, ?)
    """, (title, created_at, created_at))

    chat_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return chat_id


# -----------------------------------
# RENAME CHAT
# -----------------------------------

def rename_chat(chat_id, new_title):

    new_title = new_title.strip()

    if not new_title:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE chat_sessions
        SET title = ?
        WHERE id = ?
    """, (new_title, chat_id))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated


# -----------------------------------
# ADD MESSAGE
# -----------------------------------

def add_message(chat_id, role, content):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO chat_messages
        (chat_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (chat_id, role, content, created_at))

    cursor.execute("""
        UPDATE chat_sessions
        SET updated_at = ?
        WHERE id = ?
    """, (created_at, chat_id))

    connection.commit()
    connection.close()


# -----------------------------------
# UPDATE EXISTING MESSAGE
# -----------------------------------

def update_message(message_id, new_content):

    connection = get_connection()
    cursor = connection.cursor()

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE chat_messages
        SET content = ?,
            feedback = NULL,
            created_at = ?
        WHERE id = ?
        AND role = 'assistant'
    """, (new_content, updated_at, message_id))

    updated = cursor.rowcount > 0

    if updated:

        cursor.execute("""
            UPDATE chat_sessions
            SET updated_at = ?
            WHERE id = (
                SELECT chat_id
                FROM chat_messages
                WHERE id = ?
            )
        """, (updated_at, message_id))

    connection.commit()
    connection.close()

    return updated


# -----------------------------------
# GET ALL CHATS
# -----------------------------------

def get_chats():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, created_at, updated_at
        FROM chat_sessions
        ORDER BY updated_at DESC, id DESC
    """)

    chats = cursor.fetchall()

    connection.close()

    return chats


# -----------------------------------
# GET CHAT MESSAGES
# -----------------------------------

def get_chat_messages(chat_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, role, content, feedback, created_at
        FROM chat_messages
        WHERE chat_id = ?
        ORDER BY id
    """, (chat_id,))

    messages = cursor.fetchall()

    connection.close()

    return messages


# -----------------------------------
# SAVE MESSAGE FEEDBACK
# -----------------------------------

def save_message_feedback(message_id, feedback):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE chat_messages
        SET feedback = ?
        WHERE id = ?
    """, (feedback, message_id))

    connection.commit()
    connection.close()


# -----------------------------------
# DELETE CHAT
# -----------------------------------

def delete_chat(chat_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM chat_sessions
        WHERE id = ?
    """, (chat_id,))

    connection.commit()
    connection.close()


# -----------------------------------
# CLEAR ALL CHATS
# -----------------------------------

def clear_chats():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM chat_sessions")

    connection.commit()
    connection.close()


# -----------------------------------
# DASHBOARD STATISTICS
# -----------------------------------

def get_statistics():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM chat_sessions
    """)

    total_conversations = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM chat_messages
    """)

    total_messages = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM chat_messages
        WHERE role = 'user'
    """)

    total_questions = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM chat_messages
        WHERE role = 'assistant'
    """)

    total_responses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM chat_messages
        WHERE feedback = 'Helpful'
    """)

    helpful_feedback = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM chat_messages
        WHERE feedback = 'Not Helpful'
    """)

    not_helpful_feedback = cursor.fetchone()[0]

    connection.close()

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "total_questions": total_questions,
        "total_responses": total_responses,
        "helpful_feedback": helpful_feedback,
        "not_helpful_feedback": not_helpful_feedback
    }


# -----------------------------------
# LEGACY DATABASE FUNCTIONS
# -----------------------------------

def save_interaction(feature, user_input, response):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO conversations
        (feature, user_input, response, created_at)
        VALUES (?, ?, ?, ?)
    """, (feature, user_input, response, created_at))

    connection.commit()
    connection.close()


def get_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, feature, user_input, response,
               feedback, created_at
        FROM conversations
        ORDER BY id DESC
    """)

    history = cursor.fetchall()

    connection.close()

    return history


def save_feedback(conversation_id, feedback):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE conversations
        SET feedback = ?
        WHERE id = ?
    """, (feedback, conversation_id))

    connection.commit()
    connection.close()


def delete_conversation(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM conversations
        WHERE id = ?
    """, (conversation_id,))

    connection.commit()
    connection.close()


def clear_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM conversations")

    connection.commit()
    connection.close()
