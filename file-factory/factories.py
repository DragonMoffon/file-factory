from typing import Any, IO as _IO
from types import ModuleType
import importlib.resources as pkg

type IO = _IO[bytes] | _IO[str]
type Source = str | ModuleType

class FileFactoryBase:
    def __call__(self, name: str, sub: tuple[str, ...] = (), **kwargs) -> Any:
        pass


class FileOpener(FileFactoryBase):
    """
    Create a reusable function for opening files of a particular type at a particular location
    Can also set new defaults for the `open` function used internally.

    See `open` for other arguments

    :param anchor: The location to open at, as a module from `import <x>`.
    :param file_extension: The file extension expected to open. can be `.<extension>` or  `<extension>` or `None`.
        If None is provided then the extension must included in the file name when calling the returned function
    :return: A function which creates a context manager around an opened file
    """

    def __init__(self, source: Source, extension: str | None = None, *, mode: str = "r", buffering: int = -1, encoding: str | None = None, errors: str | None = None, newline: str | None = None) -> None:
        pass

    def __call__(self, name: str, sub: tuple[str, ...] = (), **kwargs) -> _IO[bytes] | _IO[str]:
        pass