import socket
import struct
import os
import time

from config.service_config import CDH_IP, CDH_RECEIVE_PORT, COMMS_SEND_PORT, COMMS_RECEIVE_PORT
from utils.CPU_monitor import CPUMonitor
from utils.database_logger import InfluxDBLogger
import pyfiglet


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

class CDHService:
    def __init__(self, ip=CDH_IP, port=CDH_RECEIVE_PORT):
        self.ip = ip
        self.port = port
        self.sock = None
        self.running = False
        self._setup_socket()
        self.CPU_monitor = CPUMonitor()
        self.database_logger = InfluxDBLogger()
        self.clear_console()
        self.fig2 = pyfiglet.figlet_format("CDH", font="slant")
    def clear_console(self):
        os.system('clear')  # or os.system('cls') for Windows

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
        self.clear_console()
        # logger.info(f"CDHService started, listening on {self.ip}:{self.port}")
        while self.running:
            try:
                self.print_to_console()
                data, addr = self.sock.recvfrom(1024)
                self.log_to_influxdb(self.port, addr[1], data, addr)
                if data:
                    # logger.info(f"Received data from {addr}: {data}")
                    self._process_packet(data, addr)
            except socket.timeout:
                # logger.warning("Socket timeout, no data received")
                continue
            except socket.error as e:
                # logger.error(f"Socket error: {e}")
                self.stop()
                break
            except Exception as e:
                # logger.error(f"Unexpected error: {e}")
                self.stop()
                break
            
            time.sleep(0.1)
            
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
            # logger.error(f"Unexpected error processing packet from {addr}: {e}")
            pass

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
            # logger.info("CDHService socket closed")
    def print_to_console(self):
        # Move cursor to the top-left
        print("\033[H", end="")

        # Print your data
        red = "\033[38;5;196m"
        reset = "\033[0m"
        print(f"{red}{self.fig2}{reset}")
        print("Ground-Based Recording of Important Telemetry Stuff")
        print("{:<18}{:>10}".format("CPU Temperature:", "{:6.2f}°C".format(self.CPU_monitor.get_temperature())))
        print("{:<18}{:>10}".format("CPU Frequency:", "{:6.2f} MHz".format(self.CPU_monitor.get_frequency())))
        print("{:<18}{:>10}".format("CPU Voltage:", "{:6.2f} V".format(self.CPU_monitor.get_voltage())))
        print("{:<18}{:>10}".format("CPU Load:", "{:6.2f}%".format(self.CPU_monitor.get_cpu_load())))

    def log_to_influxdb(self, dest_port, source_port, payload, addr):
        packet_struct = {
            "timestamp": time.time(),
            "CPU_temperature": self.CPU_monitor.get_temperature(),
            "CPU_frequency": self.CPU_monitor.get_frequency(),
            "CPU_voltage": self.CPU_monitor.get_voltage(),
            "CPU_load": self.CPU_monitor.get_cpu_load()
        }
        self.database_logger.log(packet_struct)
        

if __name__ == "__main__":
    try:

        cdh_service = CDHService()
        cdh_service.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # logger.error(f"Failed to start CDHService: {e}")
        pass
    finally:
        cdh_service.stop()
