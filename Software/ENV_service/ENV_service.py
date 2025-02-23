
import struct
from ENV_utils import printer
from ENV_config.ENV_service_config import FORMAT

# Format: four 4-byte integers


def main():
    # Pack four numbers into raw bytes
    numbers = struct.pack(FORMAT, 10, 20, 0, 40,2,3,32,2,3,2,323)
    
    # Show the raw bytes
    print("Raw bytes:", numbers)
    print("Byte length:", len(numbers))
    
    # Pass to printer
    printer.print_numbers(numbers)

if __name__ == "__main__":
    main()
