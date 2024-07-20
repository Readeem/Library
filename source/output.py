from __future__ import annotations

from typing import Any

__all__ = (
    'Output',
)


class _AnsiType(type):
    def __new__(
            cls,
            name: str,
            bases: tuple[type, ...],
            attrs: dict[str, Any]
    ) -> _AnsiType:
        names: list[str] = [name for name in attrs if not name.startswith('_')]
        for name in names:
            value = attrs[name]
            if not isinstance(value, int):
                continue
            attrs[name] = '\033[' + str(value) + 'm'
        return super().__new__(cls, name, bases, attrs)


class Back(metaclass=_AnsiType):
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 49


class Fore(metaclass=_AnsiType):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39


class Style(metaclass=_AnsiType):
    BRIGHT = 1
    DIM = 2
    NORMAL = 22
    RESET_ALL = 0


class Output:
    def __init__(
            self, *,
            use_color: bool = True
    ) -> None:
        self.use_color: bool = use_color

    def info(self, text: str) -> None:
        if self.use_color:
            text = f'{Style.RESET_ALL}{Fore.GREEN}{text}{Style.RESET_ALL}'
        print(text)

    def warning(self, text: str) -> None:
        if self.use_color:
            text = f'{Style.RESET_ALL}{Fore.YELLOW}{Style.BRIGHT}{text}{Style.RESET_ALL}'
        print(text)

    def error(self, text: str) -> None:
        if self.use_color:
            text = f'{Style.RESET_ALL}{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}'
        print(text)
