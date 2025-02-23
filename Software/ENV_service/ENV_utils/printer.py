# printer.py

import struct
from ENV_config.ENV_service_config import FORMAT
# By default, we'll assume the format is the same as in main.py
FORMAT = 'fffiiiffiif'

def print_numbers(data):
    """
    Unpacks the given bytes (data) into integers using FORMAT
    and prints them out.
    """
    numbers = struct.unpack(FORMAT, data)
    print("Unpacked numbers:", numbers)
