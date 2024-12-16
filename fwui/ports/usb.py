from os import path
from typing import Optional
from glob import glob

class USBPortInfo:
    devpath: str
    filecache: dict[str, str]

    def __init__(self, devpath: str):
        super().__init__()
        self.devpath = devpath
        self.filecache = {}

    def read_subfile(self, file: str) -> str:
        if file in self.filecache:
            return self.filecache[file]
        res = self._read_subfile(file)
        self.filecache[file] = res
        return res

    def _read_subfile(self, file: str) -> str:
        devfile = path.join(self.devpath, file)
        globs = glob(devfile)
        if not globs:
            return ""
        devfile = globs[0]

        try:
            with open(devfile, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return ""

    def read_int_subfile(self, file: str, base: int = 10) -> Optional[int]:
        value = self.read_subfile(file)
        if not value:
            return None
        return int(value, base)

    @property
    def vid(self) -> Optional[int]:
        return self.read_int_subfile("idVendor", 16)

    @property
    def pid(self) -> Optional[int]:
        return self.read_int_subfile("idProduct", 16)

    @property
    def speed(self) -> Optional[int]:
        return self.read_int_subfile("speed")

class USBPort:
    subdevs: list[str]

    def __init__(self, subdevs: list[str]):
        super().__init__()
        self.subdevs = subdevs

    def get_info(self) -> Optional[USBPortInfo]:
        for subdev in self.subdevs:
            info = USBPortInfo(subdev)
            if info.vid and info.pid:
                return info

        return None
