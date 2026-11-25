
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from database import db


class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for each test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test.db"

        self.patcher = patch.object(db, "DB_PATH", self.test_db_path)
        self.patcher.start()

        db.init_db()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    # -------------------------------
    # LEGACY DATABASE TESTS
    # -------------------------------

    def test_database_creation(self):
        self.assertTrue(self.test_db_path.exists())

    def test_save_interaction(self):
        db.save_interaction(
            "Ask AI",
            "What is Python?",
            "Python is a programming language."
        )

        history = db.get_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][2], "What is Python?")

    def test_save_feedback(self):
        db.save_interaction(
            "Ask AI",
            "What is AI?",
            "AI means Artificial Intelligence."
        )

        conversation_id = db.get_history()[0][0]

        db.save_feedback(conversation_id, "Helpful")

        history = db.get_history()

        self.assertEqual(history[0][4], "Helpful")

    def test_delete_conversation(self):
        db.save_interaction("Ask AI", "Question", "Answer")

        conversation_id = db.get_history()[0][0]

        db.delete_conversation(conversation_id)

        self.assertEqual(len(db.get_history()), 0)

    def test_clear_history(self):
        db.save_interaction("Ask AI", "Q1", "A1")
        db.save_interaction("Ask AI", "Q2", "A2")

        db.clear_history()

        self.assertEqual(len(db.get_history()), 0)

    # -------------------------------
    # NEW CHAT THREAD TESTS
    # -------------------------------

    def test_create_chat(self):
        chat_id = db.create_chat("Python Questions")

        chats = db.get_chats()

        self.assertIsNotNone(chat_id)
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0][1], "Python Questions")

    def test_save_multiple_messages_in_chat(self):
        chat_id = db.create_chat("AI Questions")

        db.add_message(chat_id, "user", "What is AI?")
        db.add_message(chat_id, "assistant", "AI means Artificial Intelligence.")
        db.add_message(chat_id, "user", "What is ML?")
        db.add_message(chat_id, "assistant", "ML is a branch of AI.")

        messages = db.get_chat_messages(chat_id)

        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0][1], "user")
        self.assertEqual(messages[1][1], "assistant")
        self.assertEqual(messages[2][1], "user")
        self.assertEqual(messages[3][1], "assistant")

    def test_save_message_feedback(self):
        chat_id = db.create_chat("Feedback Test")

        db.add_message(chat_id, "user", "What is Python?")
        db.add_message(chat_id, "assistant", "Python is a programming language.")

        messages = db.get_chat_messages(chat_id)
        assistant_message_id = messages[1][0]

        db.save_message_feedback(assistant_message_id, "Helpful")

        updated_messages = db.get_chat_messages(chat_id)

        self.assertEqual(updated_messages[1][3], "Helpful")

    def test_delete_chat_and_messages(self):
        chat_id = db.create_chat("Delete Test")

        db.add_message(chat_id, "user", "Hello")
        db.add_message(chat_id, "assistant", "Hi!")

        db.delete_chat(chat_id)

        self.assertEqual(db.get_chat_messages(chat_id), [])
        self.assertEqual(len(db.get_chats()), 0)

    def test_clear_chats(self):
        chat1 = db.create_chat("Chat One")
        chat2 = db.create_chat("Chat Two")

        db.add_message(chat1, "user", "Hello")
        db.add_message(chat2, "user", "Hi")

        db.clear_chats()

        self.assertEqual(len(db.get_chats()), 0)
        self.assertEqual(db.get_chat_messages(chat1), [])
        self.assertEqual(db.get_chat_messages(chat2), [])


if __name__ == "__main__":
    unittest.main()
