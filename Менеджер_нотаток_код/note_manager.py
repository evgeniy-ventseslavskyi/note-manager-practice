"""Основна бізнес-логіка консольного менеджера нотаток."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Note:
    id: int
    title: str
    text: str
    category: str
    created_at: str


class NoteManager:
    """Створює, шукає, видаляє та зберігає нотатки у JSON."""

    def __init__(self, data_file: str | Path = "data/notes.json") -> None:
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.notes = self._load()

    def _load(self) -> list[Note]:
        if not self.data_file.exists():
            return []
        try:
            data = json.loads(self.data_file.read_text(encoding="utf-8"))
            return [Note(**item) for item in data]
        except (json.JSONDecodeError, TypeError, KeyError):
            logging.exception("Не вдалося прочитати файл даних")
            return []

    def _save(self) -> None:
        data = [asdict(note) for note in self.notes]
        self.data_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, title: str, text: str, category: str) -> Note:
        """Додає нотатку після перевірки обов'язкових полів."""
        if not title.strip() or not text.strip():
            raise ValueError("Назва і текст не можуть бути порожніми")
        note = Note(
            id=max((item.id for item in self.notes), default=0) + 1,
            title=title.strip(),
            text=text.strip(),
            category=category.strip() or "Без категорії",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        self.notes.append(note)
        self._save()
        logging.info("Створено нотатку id=%s", note.id)
        return note

    def search(self, query: str) -> list[Note]:
        """Шукає без урахування регістру у назві, тексті та категорії."""
        query = query.strip().lower()
        return [
            note
            for note in self.notes
            if query in f"{note.title} {note.text} {note.category}".lower()
        ]

    def delete(self, note_id: int) -> bool:
        """Видаляє нотатку за ідентифікатором."""
        before = len(self.notes)
        self.notes = [note for note in self.notes if note.id != note_id]
        if len(self.notes) == before:
            return False
        self._save()
        logging.info("Видалено нотатку id=%s", note_id)
        return True

