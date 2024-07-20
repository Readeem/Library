from __future__ import annotations

import os
from enum import Enum
from typing import Any

__all__ = (
    'BookStatus',
    'Book'
)


class BookStatus(Enum):
    """Book status.

    Attributes
    ----------
    in_stock: BookStatus
        Book currently in the library.
    handed_over: BookStatus
        Book has been given away and not in the library.
    """
    in_stock = 1
    handed_over = 0


class Book:
    """Represents a book in the library.

    Attributes
    ----------
    title: str
        Book title.
    author: str
        Name of this book's author.
    year: int
        Number that represents the year this book was published.
    status: BookStatus
        Enum representing this book's status in the library.
    id: str
        Unique identifier of this book.
    """
    def __init__(
            self, *,
            title: str,
            author: str,
            year: int,
            status: BookStatus | None = None,
            id: str | None = None
    ) -> None:
        self.title: str = title
        self.author: str = author
        self.year: int = year
        self.status: BookStatus = status or BookStatus.in_stock
        self.id: str = id or os.urandom(6).hex()

    def __repr__(self) -> str:
        return f'<Book title={self.title} author={self.author} year={self.year} status={self.status} id={self.id}>'

    def str_status(self) -> str:
        """Returns readable string version of the status."""
        if self.status is BookStatus.in_stock:
            return 'In stock'
        elif self.status is BookStatus.handed_over:
            return 'Handed over'
        else:
            return 'Unknown status'

    def to_dict(self) -> dict[str, Any]:
        """Converts this Book to JSON serializable object."""
        return {
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'status': self.status.value,
            'id': self.id
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], /) -> Book:
        """Converts a JSON object representing this Book to a Python class instance."""
        return cls(
            title=data['title'],
            author=data['author'],
            year=int(data['year']),
            status=BookStatus(int(data['status'])),
            id=data['id']
        )
