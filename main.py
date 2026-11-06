"""Консольний інтерфейс застосунку «Менеджер нотаток»."""

import logging

from note_manager import Note, NoteManager


def show(notes: list[Note]) -> None:
    if not notes:
        print("Нотаток не знайдено.")
        return
    for note in notes:
        print(f"\n[{note.id}] {note.title} | {note.category} | {note.created_at}")
        print(note.text)


def run() -> None:
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )
    manager = NoteManager()
    actions = {
        "1": "Додати нотатку",
        "2": "Показати всі",
        "3": "Знайти",
        "4": "Видалити",
        "0": "Вийти",
    }
    while True:
        print("\n=== МЕНЕДЖЕР НОТАТОК ===")
        for key, label in actions.items():
            print(f"{key}. {label}")
        choice = input("Оберіть дію: ").strip()
        try:
            if choice == "1":
                note = manager.add(
                    input("Назва: "), input("Текст: "), input("Категорія: ")
                )
                print(f"Нотатку #{note.id} збережено.")
            elif choice == "2":
                show(manager.notes)
            elif choice == "3":
                show(manager.search(input("Пошуковий запит: ")))
            elif choice == "4":
                deleted = manager.delete(int(input("ID нотатки: ")))
                print("Нотатку видалено." if deleted else "Нотатку не знайдено.")
            elif choice == "0":
                print("До побачення!")
                break
            else:
                print("Невідома команда.")
        except ValueError as error:
            print(f"Помилка: {error}")


if __name__ == "__main__":
    run()

