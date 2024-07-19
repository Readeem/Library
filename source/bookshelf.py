import json
import os.path
from typing import Final, Any

from .book import Book


class Bookshelf:
    DATA_FILE: Final[str] = 'books.json'

    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.load_books()

    def _json_default(self, obj: Any) -> Any:
        if isinstance(obj, Book):
            return obj.to_dict()
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

    def load_books(self) -> None:
        if not os.path.exists(self.DATA_FILE):
            return

        with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
            data: dict[str, dict[str, Any]] = json.load(f)

        if not isinstance(data, dict):
            os.remove(self.DATA_FILE)
            raise TypeError(f'Invalid data in file "{self.DATA_FILE}"')

        for obj in data.values():
            try:
                book = Book.from_dict(obj)
            except (KeyError, ValueError):
                continue
            self.books[book.id] = book

    def save_books(self) -> None:
        dump: str = json.dumps(
            self.books,
            default=self._json_default,
            indent=2
        )
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(dump)

    def add_book(self, book: Book) -> None:
        self.books[book.id] = book
        self.save_books()

    def get_book(self, book_id: str) -> Book | None:
        return self.books.get(book_id)

    def remove_book(self, book_id: str) -> Book:
        book = self.books.pop(book_id)
        self.save_books()
        return book
