from __future__ import annotations

import inspect
from typing import Callable, Optional, get_args, Any
from .output import Output

__all__ = (
    'Command',
    'command'
)

OPTIONALS = frozenset({Optional[str], Optional[int], Optional[float], Optional[bool]})
TRUE_EXPRESSIONS = frozenset({'true', 'yes', '1', 't', 'y'})
FALSE_EXPRESSIONS = frozenset({'false', 'no', '0', 'f', 'n'})
CommandFunc = Callable


class Command:
    """Represents a command for this app.

    This can be constructed using `command` decorator.
    Callback function of the command must have all parameters (except self)
    typehinted with acceptable type (one of str, int, float, bool).
    Only positional parameters are allowed.
    """
    def __init__(
            self,
            func: CommandFunc,
            *,
            name: str,
            description: str | None = None,
            aliases: list[str] | None = None
    ) -> None:
        self.func: CommandFunc = self._validate_func(func)
        self.name: str = name
        self.description: str | None = description
        self.aliases: list[str] | None = aliases
        self._parameters: list[inspect.Parameter] = self._get_valid_arguments(func)

    @property
    def invokable_names(self) -> tuple[str, ...]:
        """Returns a tuple of names with which this command can be invoked."""
        if self.aliases:
            return self.name, *self.aliases
        return self.name,

    @property
    def parameters(self) -> list[str]:
        """Returns list of formatted parameters that this command accepts."""
        return [self._format_param(param) for param in self._parameters]

    def _validate_func(self, func: CommandFunc) -> CommandFunc:
        if isinstance(func, classmethod):
            raise TypeError('Console command cannot be a classmethod.')

        if isinstance(func, staticmethod):
            raise TypeError('Console command cannot be a staticmethod.')

        params = list(inspect.signature(func).parameters.values())
        valid_types = {str, int, float, bool} | OPTIONALS

        for param in params:
            if param.name == 'self' or param.kind is param.VAR_POSITIONAL:
                continue

            if param.kind is param.VAR_KEYWORD or param.kind is param.KEYWORD_ONLY:
                raise TypeError(
                    f'Console command cannot contain keyword arguments (wrong argument: {param.name}).'
                    f' in function {func.__name__}'
                )

            if param.annotation not in valid_types or not hasattr(param.annotation, '__name__'):
                raise TypeError(
                    f'Console command must have all parameters annotated with one of: str, int, float, bool'
                    f' or typing.Optional[str | int | float | bool]'
                    f' (except self and "*" parameters)'
                    f' (wrong argument: {param.name})'
                    f' in function {func.__name__}'
                )
        return func

    def _get_valid_arguments(self, func: CommandFunc) -> list[inspect.Parameter]:
        return [
            param
            for param in inspect.signature(func).parameters.values()
            if self._check_param(param)
        ]

    def _get_required_count(self) -> int:
        return sum(
            1 for param in self._parameters
            if param.annotation not in OPTIONALS
        )

    def _check_param(self, param: inspect.Parameter) -> bool:
        return (
                param.kind is param.POSITIONAL_OR_KEYWORD
                or param.kind is param.POSITIONAL_ONLY
                or param.kind is param.VAR_POSITIONAL
        ) and param.name != 'self'

    def _print_usage(self, output: Output) -> None:
        u = ' '.join(self._format_param(param) for param in self._parameters)
        output.error(f'Usage: {" | ".join(self.invokable_names)} {u}')

    def _print_expected(self, name: str, expected: type, given: str, output: Output) -> None:
        output.error(f'Expected "{name}" argument to be {expected.__name__}, got "{given}"')

    def _format_param(self, param: inspect.Parameter) -> str:
        return f'<{param.name}: {param.annotation.__name__ if param.annotation not in OPTIONALS else param.annotation}>'

    def invoke(self, cls: Any, params: list[str], *, output: Output) -> None:
        """Invoke this command's callback.

        Parameters
        ----------
        cls: Any
            The class instance that holds the command (self in command parameters)
        params: list[str]
            Raw parameters for this command entered by user.
        output: Output
            The output for this command.
        """
        ready = []
        for i, given in enumerate(params):
            if not self._parameters:
                break
            try:
                p = self._parameters[i]
            except IndexError:
                p = self._parameters[-1]
                if p.kind is not p.VAR_POSITIONAL:
                    break
            if p.kind is p.VAR_POSITIONAL:
                ready.append(given)
                continue

            _type = p.annotation if p.annotation not in OPTIONALS else get_args(p.annotation)[0]
            if _type is bool:
                if given in TRUE_EXPRESSIONS:
                    given = 1
                elif given in FALSE_EXPRESSIONS:
                    given = 0
            try:
                ready.append(_type(given))
            except (TypeError, ValueError):
                return self._print_expected(p.name, _type, given, output)

        if len(ready) < self._get_required_count():
            return self._print_usage(output)
        try:
            self.func(cls, *ready)
        except Exception as e:
            output.error(str(e))


class SupportsCommandsType(type):
    """Metaclass for commands support.

    This metaclass must be used on a class where you want support for the commands.
    This will add a class variable `COMMANDS` which will hold all defined commands
    in this class as a list of `Command`.
    """
    def __new__(
            metacls,
            name: str,
            bases: tuple[type, ...],
            attrs: dict[str, Any]
    ) -> SupportsCommandsType:
        commands = []
        for value in attrs.values():
            if isinstance(value, Command):
                commands.append(value)
        attrs['COMMANDS'] = commands
        return super().__new__(metacls, name, bases, attrs)


def command(
        *,
        name: str | None = None,
        description: str | None = None,
        aliases: list[str] | None = None
) -> Callable[[Callable], Command]:
    """Decorator that converts function to the command.

    Parameters
    ----------
    name: str | None
        Optional command name.
        If not provided this will be the function name.
    description: str | None
        Optional command description.
        If not provided this will be the function docstring.
    aliases: list[str] | None
        Optional list of aliases for this command.
    """
    def decorator(func: Callable) -> Command:
        return Command(
            func,
            name=name or func.__name__,
            description=description or func.__doc__,
            aliases=aliases
        )
    return decorator
