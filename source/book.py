from __future__ import annotations

import os
from enum import Enum
from typing import Any

__all__ = (
    'BookStatus',
    'Book'
)


class BookStatus(Enum):
    in_stock = 1
    handed_over = 0


class Book:
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
        self.id: str = id or os.urandom(4).hex()

    def __repr__(self) -> str:
        return f'<Book title={self.title} author={self.author} year={self.year} status={self.status} id={self.id}>'

    def str_status(self) -> str:
        if self.status is BookStatus.in_stock:
            return 'In stock'
        elif self.status is BookStatus.handed_over:
            return 'Handed over'
        else:
            return 'Unknown status'

    def to_dict(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'status': self.status.value,
            'id': self.id
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], /) -> Book:
        return cls(
            title=data['title'],
            author=data['author'],
            year=int(data['year']),
            status=BookStatus(int(data['status'])),
            id=data['id']
        )
