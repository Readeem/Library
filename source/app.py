import os
import sys
from typing import ClassVar

from .command import Command, SupportsCommandsType
from .output import Output


class App(metaclass=SupportsCommandsType):
    COMMANDS: ClassVar[list[Command]]

    def __init__(self) -> None:
        self.output: Output = Output()

    @staticmethod
    def preload() -> None:
        if sys.platform == 'win32':
            os.system('title Library Control')

    @staticmethod
    def clear_screen() -> None:
        """Function to clear the screen. Platform-independent."""
        clear_cmd = 'cls' if sys.platform == 'win32' else 'clear'
        os.system(clear_cmd)

    def invoke_command(self, name: str, params: list[str]) -> None:
        for command in self.COMMANDS:
            if name in command.invokable_names:
                command.invoke(params, output=self.output)
                return
        self.output.error(f'Unknown command: "{name}"')

    def tick(self) -> None:
        self.clear_screen()
        print('This is Library Control app. Enter command.')
        params: list[str] = input('> ').strip().split()
        if not params:
            # User entered nothing, reset
            return
        name: str = params[0]
        self.invoke_command(name, params[1:])
        input('Press Enter to continue...')

    def run(self) -> None:
        self.preload()
        try:
            while True:
                self.tick()
        except KeyboardInterrupt:
            pass
