from os import path

class ChargePort:
    devnode: str

    def __init__(self, devnode: str):
        self.devnode = devnode

    def read_number_file(self, file: str) -> int:
        with open(path.join(self.devnode, file), "r") as f:
            return int(f.read(), 10)
        
    def current(self) -> int:
        return self.read_number_file("current_now")
    
    def voltage(self) -> int:
        return self.read_number_file("voltage_now")

    def online(self) -> bool:
        return self.read_number_file("online") == 1
