import socket
import struct
# import logging
import time

from config.service_config import CDH_IP, CDH_SEND_PORT, CDH_RECIEVE_PORT, COMMS_SEND_PORT, COMMS_RECIEVE_PORT
from utils.CPU_monitor import CPUMonitor
import pyfiglet

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

class CDHService:
    def __init__(self, ip=CDH_IP, port=CDH_RECIEVE_PORT):
        self.ip = ip
        self.port = port
        self.sock = None
        self.running = False
        self._setup_socket()
        self.CPU_monitor = CPUMonitor()
    def _setup_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
            self.sock.settimeout(0.5)  # set a 0.5 second timeout
            # logger.info(f"CDHService listening on {self.ip}:{self.port}")
        except Exception as e:
            # logger.error(f"Error initializing socket: {e}")
            raise
   
    def start(self):
        self.running = True
        # ANSI escape codes for orange text (using color code 208) and reset
        orange = "\033[38;5;208m"
        reset = "\033[0m"

        # Generate and print figlet text for "GRITS"
        fig = pyfiglet.figlet_format("GRITS", font="banner")
        print(f"{orange}{fig}{reset}")
        print()
        # Print the subtitle in smaller letters
        print("Ground-Based Recording of Important Telemetry Stuff")
        # logger.info(f"CDHService started, listening on {self.ip}:{self.port}")
        while self.running:
            try:
                print("______________________________________")
                print("CPU Temperature: {:.2f}°C".format(self.CPU_monitor.get_temperature()))
                print("CPU Frequency: {:.2f} MHz".format(self.CPU_monitor.get_frequency()))
                print("CPU Voltage: {:.2f} V".format(self.CPU_monitor.get_voltage()))
                print("CPU Load: {:.2f}%".format(self.CPU_monitor.get_cpu_load()))
                
                data, addr = self.sock.recvfrom(1024)
                if data:
                    # logger.info(f"Received data from {addr}: {data}")
                    self._process_packet(data, addr)
            except Exception as e:
                # logger.error(f"Error receiving data: {e}")
                pass
            
            time.sleep(0.01)
            
    def _process_packet(self, data, addr):
        try:
            if len(data) < 4:
                # logger.warning(f"Received packet too short from {addr}: {len(data)} bytes")
                return
            # Unpack the 4-byte header: dest_port and source_port
            dest_port, source_port = struct.unpack("!HH", data[:4])
            payload = data[4:]
            msg = (
                f"CDH Received from {addr[0]}:{addr[1]} | "
                f"Source Port: {source_port}, Dest Port: {dest_port} | "
                f"Payload: {payload.hex()} ({len(payload)} bytes)"
            )
            # logger.info(msg)
            # Print to console
            print(msg)
        except struct.error as e:
            # logger.error(f"Error unpacking header from {addr}: {e}")
            pass
        except Exception as e:
            # logger.error(f"Error processing packet from {addr}: {e}")
            pass

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
            # logger.info("CDHService socket closed")

if __name__ == "__main__":
    try:
        cdh_service = CDHService()
        cdh_service.start()
    except KeyboardInterrupt:
        # logger.info("Shutting down CDHService")
        cdh_service.stop()
    except Exception as e:
        # logger.error(f"Failed to start CDHService: {e}")
        pass