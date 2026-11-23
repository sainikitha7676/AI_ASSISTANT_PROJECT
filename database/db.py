
import sqlite3
from pathlib import Path
from datetime import datetime


# Database file location
DB_PATH = Path(__file__).resolve().parent / "assistant.db"


# ---------------- DATABASE CONNECTION ----------------

def get_connection():
    return sqlite3.connect(DB_PATH)


# ---------------- CREATE DATABASE TABLE ----------------

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

    connection.commit()
    connection.close()


# ---------------- SAVE CONVERSATION ----------------

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


# ---------------- GET CONVERSATION HISTORY ----------------

def get_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, feature, user_input, response, feedback, created_at
        FROM conversations
        ORDER BY id DESC
    """)

    history = cursor.fetchall()
    connection.close()

    return history


# ---------------- SAVE FEEDBACK ----------------

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
