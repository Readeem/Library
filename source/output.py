from __future__ import annotations

import os
import sys
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
        self.use_color: bool = use_color and self.is_color_supported()

    @staticmethod
    def is_color_supported() -> bool:
        """Return True if the terminal device supports color output.

        Returns
        -------
        bool
            True if color is allowed on the output terminal, False otherwise.
        """
        # isatty is not always implemented, https://code.djangoproject.com/ticket/6223
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

        clicolor = os.environ.get('CLICOLOR')
        if os.environ.get('CLICOLOR_FORCE', '0') != '0':
            # https://bixense.com/clicolors/
            return True
        if clicolor is not None and clicolor != '0' and is_a_tty:
            # https://bixense.com/clicolors/
            return True
        if clicolor == '0':
            # https://bixense.com/clicolors/
            return False
        if os.environ.get('COLORTERM', '').casefold() in ('truecolor', '24bit'):
            # Seems to be used by Gnome Terminal.
            # https://gist.github.com/XVilka/8346728#true-color-detection
            return True

        plat = sys.platform
        if plat == 'Pocket PC':
            return False

        if plat == 'win32':
            color_support = os.environ.get('TERM_PROGRAM') in ('mintty', 'Terminus')
            color_support |= 'ANSICON' in os.environ
            color_support &= is_a_tty
        else:
            color_support = is_a_tty

        color_support |= bool(os.environ.keys() & {'PYCHARM_HOSTED', 'WT_SESSION'})
        return color_support

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
