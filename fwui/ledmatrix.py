from serial import Serial

LED_MATRIX_COLS = 9
LED_MATRIX_ROWS = 34

class LEDMatrix:
    port: Serial
    is_cleared: bool = False
    id: str

    def __init__(self, id: str, port: str):
        super().__init__()
        # Baudrate doesn't matter, those are CDC serial ports
        # which do not follow any baudrate
        self.id = id
        self.port = Serial(port, timeout=5.0)
        self.clear()

    def clear(self) -> None:
        if self.is_cleared:
            return
        _ = self.port.write(b'w\x00')
        _ = self.port.write(b's\x7F')
        self.is_cleared = True

    def draw(self, bitmap: bytes, blocking: bool = True, pwm: bool = True) -> None:
        if len(bitmap) != LED_MATRIX_ROWS * LED_MATRIX_COLS:
            raise ValueError(f"Bitmap must be {LED_MATRIX_ROWS * LED_MATRIX_COLS} bytes long")

        self.is_cleared = False

        mode_char = b'm' if pwm else b'n'
        if blocking:
            mode_char = mode_char.upper()
        _ = self.port.write(mode_char + bitmap)
        if blocking:
            assert self.port.read(1) == mode_char
