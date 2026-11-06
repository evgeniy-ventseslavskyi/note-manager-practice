import json
import tempfile
import unittest
from pathlib import Path

from note_manager import NoteManager


class NoteManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "notes.json"
        self.manager = NoteManager(self.path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_and_save(self) -> None:
        note = self.manager.add("Покупки", "Купити хліб", "Особисте")
        self.assertEqual(note.id, 1)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8"))[0]["title"], "Покупки")

    def test_search_is_case_insensitive(self) -> None:
        self.manager.add("Python", "Вивчити JSON", "Навчання")
        self.assertEqual(len(self.manager.search("python")), 1)

    def test_delete(self) -> None:
        note = self.manager.add("Тест", "Текст", "Інше")
        self.assertTrue(self.manager.delete(note.id))
        self.assertEqual(self.manager.notes, [])

    def test_empty_title_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.manager.add("", "Текст", "Інше")


if __name__ == "__main__":
    unittest.main()

