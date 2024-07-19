import os
import sys
from typing import ClassVar, Callable

from .book import Book, BookStatus
from .bookshelf import Bookshelf
from .command import Command, SupportsCommandsType, command
from .output import Output


class App(metaclass=SupportsCommandsType):
    COMMANDS: ClassVar[list[Command]]

    def __init__(self) -> None:
        self.output: Output = Output()
        self.bookshelf: Bookshelf = Bookshelf()

    @command(aliases=['h'])
    def help(self) -> None:
        """Help command, shows a list of all available commands and their descriptions."""
        self.output.info('Here is a list of all available commands:\n')
        out = '====================\n'
        for cmd in self.COMMANDS:
            out += f'{" / ".join(cmd.invokable_names)}\n'
            if cmd.description:
                out += f'| {cmd.description}\n'
            if params := cmd.parameters:
                out += f'| Parameters: {" ".join(params)}\n'
            out += '====================\n'
        self.output.info(out)

    @command(aliases=['+', 'create'])
    def add(self, *title: str) -> None:
        """Command to add a new book. You will need to enter title, author and year."""
        title = ' '.join(title)
        author = self.input_flow(
            f'Let\'s add a new book "{title}"! Now enter the name of the book author.'
        )
        if not author:
            return

        def check_year(y: str) -> bool:
            try:
                number = int(y)
                if len(y) > 4 or number <= 0:
                    raise TypeError
            except (ValueError, TypeError):
                self.output.error(f'Year must be an 1-4 digit number, not "{y}"')
                return False
            return True

        year = self.input_flow(
            f'Great! Now we have a book named "{title}" written by {author},\n'
            f'but have no information about when it was published. Please tell us!',
            check_year
        )
        if not year:
            return

        self.bookshelf.add_book(
            Book(
                title=title,
                author=author,
                year=int(year)
            )
        )
        self.output.info(f'Book "{title}" written by {author} in {year} year added successfully!')

    @command(aliases=['list', 'ls', 'all'])
    def books(self) -> None:
        """Command to show all of the stored books."""
        self.output.info('Here are list of all stored books:\n')
        out = '====================\n'
        for book in self.bookshelf.books.values():
            out += f'| Book "{book.title}"\n'
            out += f'| Author: {book.author}\n'
            out += f'| {book.year} year of publishing\n'
            out += f'| ID: {book.id}\n'
            out += f'| Status: {book.str_status()}\n'
            out += '====================\n'
        self.output.info(out)

    @command()
    def status(self, book_id: str, status: str) -> None:
        """Command for changing the book status. Status parameter must be one of 'stock' and 'out'."""
        if book_id not in self.bookshelf.books:
            self.output.error(f'Book with ID "{book_id}" doesn\'t exist!')
            return
        if status not in {'stock', 'out'}:
            self.output.error('Status parameter must be one of "stock" and "out"!')
            return

        book: Book = self.bookshelf.get_book(book_id)
        assert book is not None
        book.status = BookStatus.in_stock if status == 'stock' else BookStatus.handed_over
        self.bookshelf.add_book(book)
        self.output.info(f'Status of the book "{book.title}" (ID:{book_id}) has been set to "{book.str_status()}"')

    @command(aliases=['del', 'd'])
    def delete(self, book_id: str) -> None:
        """Command to delete a book by it's ID."""
        if book_id not in self.bookshelf.books:
            self.output.error(f'Book with ID "{book_id}" doesn\'t exist!')
            return

        removed = self.bookshelf.remove_book(book_id)
        self.output.info(f'Book with ID "{book_id}" and title "{removed.title}" deleted successfully!')

    @staticmethod
    def preload() -> None:
        if sys.platform == 'win32':
            os.system('title Library')

    @staticmethod
    def clear_screen() -> None:
        """Function to clear the screen. Platform-independent."""
        clear_cmd = 'cls' if sys.platform == 'win32' else 'clear'
        os.system(clear_cmd)

    def input_flow(self, title: str, predicate: Callable[[str], bool] | None = None) -> str | None:
        title += '\nTo cancel the process enter "cancel" or "c".\n'
        while True:
            self.clear_screen()
            self.output.info(title)
            result: str = input('~ ').strip()
            if not result:
                continue
            if result in {'cancel', 'c'}:
                return None
            if predicate and not predicate(result):
                input('Press Enter to continue...\n')
                continue
            break
        return result

    def invoke_command(self, name: str, params: list[str]) -> None:
        self.clear_screen()
        for cmd in self.COMMANDS:
            if name in cmd.invokable_names:
                cmd.invoke(self, params, output=self.output)
                return
        self.output.error(f'Unknown command: "{name}"')

    def tick(self) -> None:
        self.clear_screen()
        self.output.info(
            'This is Library app.\n'
            'You can manage your books here!\n'
            'Enter a command down below. For list of available commands use "help" command.\n'
        )
        params: list[str] = input('> ').strip().split()
        if not params:
            # User entered nothing, reset
            return
        name: str = params[0]
        self.invoke_command(name, params[1:])
        input('Press Enter to continue...\n')

    def run(self) -> None:
        self.preload()
        try:
            while True:
                self.tick()
        except KeyboardInterrupt:
            self.output.warning('\nReceived signal to close the app.')
