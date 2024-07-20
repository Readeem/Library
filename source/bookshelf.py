import json
import os.path
from typing import Final, Any

from .book import Book


class Bookshelf:
    """Represents a bookshelf where books is stored.

    By default this class stores all the books in `books.json`.

    Attributes
    ----------
    DATA_FILE: Final[str]
        Name of the file where the books will be saved.
    books: dict[str, Book]
        Mapping of Book.id to Book.
    """
    DATA_FILE: Final[str] = 'books.json'

    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.load_books()

    def _json_default(self, obj: Any) -> Any:
        if isinstance(obj, Book):
            return obj.to_dict()
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

    def load_books(self) -> None:
        """Method to load books from the data file.

        If the data file is corrupted/invalid this method will remove it.
        If some book data from the file invalid it will be ignored during loading.
        """
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
            except (KeyError, ValueError, TypeError):
                continue
            self.books[book.id] = book

    def save_books(self) -> None:
        """Method to save currently cached books to the data file."""
        dump: str = json.dumps(
            self.books,
            default=self._json_default,
            indent=2
        )
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(dump)

    def add_book(self, book: Book) -> None:
        """Method to add a book.

        If the book with this ID already exists it will be overwritten.
        This method automatically saves the data to file.
        """
        self.books[book.id] = book
        self.save_books()

    def get_book(self, book_id: str) -> Book | None:
        """Method to get a book by it's id.

        Returns
        -------
        Book | None
            Book with the given id or ``None`` if not found.
        """
        return self.books.get(book_id)

    def remove_book(self, book_id: str) -> Book:
        """Removes the book with provided id.

        This method automatically saves the data to file.

        Raises
        ------
        KeyError
            Raised if the book with given id doesn't exists.

        Returns
        -------
        Book
            Book that was deleted.
        """
        book = self.books.pop(book_id)
        self.save_books()
        return book
