
import unittest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from database import db


class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = Path(self.temp_dir.name) / "test.db"

        self.patcher = patch.object(
            db, "DB_PATH", self.test_db_path
        )
        self.patcher.start()

        db.init_db()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_database_creation(self):
        self.assertTrue(self.test_db_path.exists())

    def test_save_interaction(self):
        db.save_interaction(
            "Answer Questions",
            "What is Python?",
            "Python is a programming language."
        )

        history = db.get_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][1], "Answer Questions")
        self.assertEqual(history[0][2], "What is Python?")

    def test_save_feedback(self):
        db.save_interaction(
            "Answer Questions",
            "What is AI?",
            "AI means Artificial Intelligence."
        )

        history = db.get_history()
        conversation_id = history[0][0]

        db.save_feedback(conversation_id, "Helpful")

        updated_history = db.get_history()

        self.assertEqual(updated_history[0][4], "Helpful")

    def test_delete_conversation(self):
        db.save_interaction(
            "Summarize Text",
            "Test input",
            "Test summary"
        )

        conversation_id = db.get_history()[0][0]

        db.delete_conversation(conversation_id)

        self.assertEqual(len(db.get_history()), 0)

    def test_clear_history(self):
        db.save_interaction("Feature 1", "Input 1", "Response 1")
        db.save_interaction("Feature 2", "Input 2", "Response 2")

        db.clear_history()

        self.assertEqual(len(db.get_history()), 0)


if __name__ == "__main__":
    unittest.main()
