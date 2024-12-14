# All icons should be 9x8 pixels
from usb import USBPortModule

USB_ICONS: dict[USBPortModule, list[int]] = {}

DISPLAY_CONNECTED_ICONS: dict[USBPortModule, list[int]] = {}
DISPLAY_DISCONNECTED_ICONS: dict[USBPortModule, list[int]] = {}

def parse_str_info(src: str) -> list[int]:
    res = []
    for c in src:
        if c == " ":
            res.append(0)
        elif c == "#":
            res.append(0xFF)
        elif c == "1":
            res.append(0x11)
        elif c == "2":
            res.append(0x22)
        elif c == "3":
            res.append(0x33)
        elif c == "4":
            res.append(0x44)
        elif c == "5":
            res.append(0x55)
        elif c == "6":
            res.append(0x66)
        elif c == "7":
            res.append(0x77)
        elif c == "8":
            res.append(0x88)
        elif c == "9":
            res.append(0x99)
        elif c == "A":
            res.append(0xAA)
        elif c == "B":
            res.append(0xBB)
        elif c == "C":
            res.append(0xCC)
        elif c == "D":
            res.append(0xDD)
        elif c == "E":
            res.append(0xEE)
        elif c == "F":
            res.append(0xFF)
    print(len(res))
    return res



DISPLAY_CONNECTED_ICONS[USBPortModule.HDMI] = parse_str_info(
    "   ####  " +
    "  #   #  " +
    "  # # #  " +
    "  # # #  " +
    "  # # #  " +
    "  # # #  " +
    "  #   #  " +
    "   ####  "
)

DISPLAY_CONNECTED_ICONS[USBPortModule.DISPLAY_PORT] = parse_str_info(
    "   ####  " +
    "  #   #  " +
    "  ### #  " +
    "  # # #  " +
    "  # # #  " +
    "  ### #  " +
    "  #   #  " +
    "  #####  "
)

DISPLAY_DISCONNECTED_ICONS[USBPortModule.HDMI] = parse_str_info(
    "   ####  " +
    "  #   #  " +
    "  # 3 #  " +
    "  # 3 #  " +
    "  # 3 #  " +
    "  # 3 #  " +
    "  #   #  " +
    "   ####  "
)

DISPLAY_DISCONNECTED_ICONS[USBPortModule.DISPLAY_PORT] = parse_str_info(
    "   ####  " +
    "  #   #  " +
    "  #33 #  " +
    "  # 3 #  " +
    "  # 3 #  " +
    "  #33 #  " +
    "  #   #  " +
    "  #####  "
)

USB2_ICON = parse_str_info(
    "   ###   " +
    "  #   #  " +
    "      #  " +
    "     #   " +
    "    #    " +
    "   #     " +
    "  #      " +
    "  #####  "
)

USB3_ICON = parse_str_info(
    "   ###   " +
    "  #   #  " +
    "      #  " +
    "    ##   " +
    "      #  " +
    "      #  " +
    "  #   #  " +
    "   ###   "
)

USB_ICONS[USBPortModule.USB4] = parse_str_info(
    "     #   " +
    "    ##   " +
    "   # #   " +
    "  #  #   " +
    "  #  #   " +
    "  #####  " +
    "     #   " +
    "     #   "
)

_CROSS = parse_str_info(
    " #     # " +
    "  #   #  " +
    "   # #   " +
    "    #    " +
    "    #    " +
    "   # #   " +
    "  #   #  " +
    " #     # "
)

def _make_usb_invalid_display_icon(port_module: USBPortModule) -> list[int]:
    icon = DISPLAY_DISCONNECTED_ICONS[port_module].copy()
    for i, x in enumerate(_CROSS):
        if x:
            icon[i] = x
        else:
            icon[i] //= 4
    USB_ICONS[port_module] = icon

_make_usb_invalid_display_icon(USBPortModule.HDMI)
_make_usb_invalid_display_icon(USBPortModule.DISPLAY_PORT)
