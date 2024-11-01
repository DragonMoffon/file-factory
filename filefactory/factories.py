from typing import Any, IO, Generator, Callable, Protocol
from types import ModuleType
from pathlib import Path
from contextlib import contextmanager
import importlib.resources as pkg

type Source = str | ModuleType


class FileFactoryBase:

    def __init__(self, source: Source, extension: str | None) -> None:
        self.source = source
        if extension is not None and not extension.startswith("."):
            extension = "." + extension
        self.extension = extension or ""
        with pkg.as_file(pkg.files(source)) as root_pth:
            self.root = root_pth

    def __call__(self, name: str, sub: tuple[str, ...] = (), **kwargs) -> Path:
        pass


class FileOpener(FileFactoryBase):
    """
    Create a reusable function for opening files of a particular type at a particular location
    Can also set new defaults for the `pathlib.Path.open` function used internally.

    See `Path.open` for other arguments

    Args:
        source: The location to open at, as a module from `import <x>`.
        extension: The file extension expected to open. can be `.<extension>` or  `<extension>` or `None`.
                   If None is provided then the extension must included in the file name when calling the returned function
    """

    def __init__(
        self,
        source: Source,
        extension: str | None = None,
        *,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> None:
        FileFactoryBase.__init__(self, source, extension)
        self.default_mode = mode
        self.default_buffering = buffering
        self.default_encoding = encoding
        self.default_errors = errors
        self.default_newline = newline

    def __call__(
        self,
        name: str,
        directories: tuple[str, ...] = (),
        *,
        mode: str | None = None,
        buffering: int | None = None,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> Generator[IO, None, None]:
        """
        Open a file with a predetermined location.
        Also has the arguments for `pathlib.Path.open` available. Custom defaults can be provided
        at the same time as the extension and source

        See `Path.open` for other arguments

        Args:
            name: The name of the file to open. If no file extension was provided on
                creation it must be included in the name.
            directories: Any sub directories from the root as a tuple ('<subdir1>', '<subdir2>')
        """
        if mode is None:
            mode = self.default_mode
        if buffering is None:
            buffering = self.default_buffering
        if encoding is None:
            encoding = self.default_encoding
        if errors is None:
            errors = self.default_errors
        if newline is None:
            newline = self.default_newline

        file = f"{name}{self.extension}"
        path = self.root.joinpath(*directories).joinpath(file)
        return path.open(mode, buffering, encoding, errors, newline)


class PathFinder(FileFactoryBase):
    """
    Create a reusable function for finding paths.

    Args:
        source: The location to start at, as a module from `import <x>`.
        extension: The file extension expected to find. can be `.<extension>` or  `<extension>` or `None`.
                   If None is provided then the extension must included in the file name when calling the returned function
    """

    def __init__(self, source: Source, extension: str | None) -> None:
        FileFactoryBase.__init__(source, extension)

    def __call__(self, name: str, sub: tuple[str, ...] = ()) -> Any:
        """
        Find the absolute path to the file with specified name and file extension.
        Uses the file extension provided at creation. If None was used then name
        must include the file extension

        Args:
            name: The name of the file to open. If no file extension was provided on
                creation it must be included in the name.
            sub_directory: Any sub directories from the root as a tuple ('<subdir1>', '<subdir2>')

        Returns:
            A pathlib Path object with the absolute path to the specified file
        """
        return self.root.joinpath(*sub).joinpath(f"{name}{self.extension}")


class FileProcessor[T](FileFactoryBase):

    def __init__(
        self,
        source: str | ModuleType,
        extension: str | None,
        process: Callable[..., T] = lambda i: i,
        input: str | None = None,
        *args,
        **kwds,
    ) -> None:
        FileFactoryBase.__init__(source, extension)
        self.input = input
        self.process = process
        self.args = args
        self.kwds = kwds

    def __call__(self, name: str, sub: tuple[str, ...] = (), *args, **kwds) -> T:
        file = self.root.joinpath(*sub).joinpath(f"{name}{self.extension}")
        kwds = self.kwds.update(kwds)
        if self.input is None:
            return self.process(file, *args, **kwds)
        kwds[self.input] = file
        return self.procss(*args, **kwds)


class StringOpener(FileFactoryBase):
    """
    Create a reusable function for retrieving the text from files of a particular type.

    Args:
        anchor: The location to open at, as a module from `import <x>`.
        file_extension: The file extension expected to open. can be `.<extension>` or just `<extension>`. Defaults to 'txt'
        encoding: The default text encoding to use. Defaults to 'utf-8'.
        errors: See pathlib.Path.read_text for details.

    """

    def __init__(
        self,
        source: str | ModuleType,
        extension: str | None,
        *,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> None:
        FileFactoryBase.__init__(source, extension)
        self.default_encoding = encoding
        self.default_errors = errors

    def __call__(
        self,
        name: str,
        sub: tuple[str, ...] = (),
        *,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> str:
        """
        Read the entire contents of the provided file and return it as a single sting.
        Uses the file extension provided at creation.

        Args:
            name: The name of the file WITHOUT the file extension
            sub_directories: Any sub directories from the root WITHOUT seperators ('<subdir1>', '<subdir2>')
            encoding: The text encoding to use. Defaults to the provided encoding at creation.
            errors: See pathlib.Path.read_text for details.
        """
        if encoding is None:
            encoding = self.default_encoding
        if errors is None:
            errors = self.default_errors
        return (
            self.root.joinpath(*sub)
            .joinpath(f"{name}{self.extension}")
            .read_text(encoding, errors)
        )


class ByteOpener(FileFactoryBase):
    """
    Create a reusable function for retrieving the binary from files of a particular type.

    Args:
        source: The location to open at, as a module from `import <x>`.
        extension: The file extension expected to open. can be `.<extension>` or just `<extension>`
    """

    def __call__(
        self,
        name: str,
        sub: tuple[str, ...] = (),
    ) -> bytes:
        """
        Read the entire contents of the provided file and return it as bytes.
        Uses the file extension provided at creation.

        Args:
            name: The name of the file
            sub_directories: Any sub directories from the root as a typle ('<subdir1>', '<subdir2>')

        Returns:
            The entire file as bytes
        """
        return self.root.joinpath(*sub).joinpath(f"{name}{self.extension}").read_bytes()
