from os import path
from glob import glob
from typing import overload

class DevInfo:
    _filecache: dict[str, bytes  | None]
    devpath: str

    def __init__(self, devpath: str):
        super().__init__()
        self.devpath = devpath
        self._filecache = {}

    @overload
    def read_str_subfile(self, file: str, *, default: str) -> str: ...
    @overload
    def read_str_subfile(self, file: str, *, default: None = None) -> str | None: ...

    def read_str_subfile(self, file: str, *, default: str | None = None) -> str | None:
        value = self.read_subfile(file)
        if value is None:
            return default
        return value.decode("utf-8").strip()

    def read_subfile(self, file: str) -> bytes | None:
        if file in self._filecache:
            res = self._filecache[file]
        else:
            res = self._read_subfile(file)
            self._filecache[file] = res
        return res

    def _read_subfile(self, file: str) -> bytes | None:
        devfile = path.join(self.devpath, file)
        globs = glob(devfile)
        if not globs:
            return None
        if len(globs) > 1:
            raise ValueError(f"Multiple files found for {devfile}")
        devfile = globs[0]

        try:
            with open(devfile, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    @overload
    def read_int_subfile(self, file: str, *, base: int = 10, default: int) -> int: ...
    @overload
    def read_int_subfile(self, file: str, *, base: int = 10, default: None = None) -> int | None: ...

    def read_int_subfile(self, file: str, *, base: int = 10, default: int | None = None) -> int | None:
        value = self.read_str_subfile(file)
        if value is None or value == "":
            return default
        return int(value, base)
