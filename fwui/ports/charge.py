from os import path

class ChargePort:
    devnode: str

    def __init__(self, devnode: str):
        super().__init__()
        self.devnode = devnode

    def read_number_file(self, file: str) -> int:
        with open(path.join(self.devnode, file), "r") as f:
            return int(f.read(), 10)
        
    def current(self) -> int:
        return self.read_number_file("current_now") // 1000000
    
    def voltage(self) -> int:
        return self.read_number_file("voltage_now") // 1000000

    def online(self) -> bool:
        return self.read_number_file("online") == 1
