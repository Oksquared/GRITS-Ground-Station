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
            # Allow address reuse
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try to bind to the preferred port, if fails try alternate ports
            try:
                self.sock.bind((self.ip, self.port))
            except socket.error as e:
                if e.errno == 98:  # Address already in use
                    print(f"Port {self.port} is in use, trying alternate port...")
                    # Try the next few port numbers
                    for port in range(self.port + 1, self.port + 10):
                        try:
                            self.sock.bind((self.ip, port))
                            self.port = port  # Update the port number
                            print(f"Successfully bound to port {port}")
                            break
                        except socket.error:
                            continue
                    else:
                        raise Exception("Could not find an available port")
                else:
                    raise
            
            self.sock.settimeout(0.5)  # set a 0.5 second timeout
            print(f"Socket bound to {self.ip}:{self.port}")
        except Exception as e:
            print(f"Error initializing socket: {e}")
            raise
   
    def _draw_static_ui(self):
        """Draw the static parts of the UI."""
        print("\n" + "=" * 50)
        print("\033[91mCDH SERVICE\033[0m - GRITS Ground Station")
        print("=" * 50)
        print("Ground-Based Recording of Important Telemetry Stuff")
        print("-" * 50)
        print("\nSystem Information (updates every second):\n")
        print("CPU Temperature: {}")
        print("CPU Frequency:   {}")
        print("CPU Voltage:     {}")
        print("CPU Load:        {}")
        print("\n" + "-" * 50)
        print(f"Listening on {self.ip}:{self.port} for incoming packets")
        print("Press Ctrl+C to exit")
        print("=" * 50)

    def _update_dynamic_values(self):
        """Update the dynamic values by redrawing the screen."""
        try:
            # Get system information with error handling
            try:
                temp = self.CPU_monitor.get_temperature()
                temp_str = "{:.2f}°C".format(temp) if temp >= 0 else "N/A"
            except:
                temp_str = "N/A"
                
            try:
                freq = self.CPU_monitor.get_frequency()
                freq_str = "{:.2f} MHz".format(freq) if freq >= 0 else "N/A"
            except:
                freq_str = "N/A"
                
            try:
                volt = self.CPU_monitor.get_voltage()
                volt_str = "{:.2f} V".format(volt) if volt >= 0 else "N/A"
            except:
                volt_str = "N/A"
                
            try:
                load = self.CPU_monitor.get_cpu_load()
                load_str = "{:.2f}%".format(load) if load >= 0 else "N/A"
            except:
                load_str = "N/A"
            
            # Clear screen and redraw with current values
            self.clear_console()
            print("\n" + "=" * 50)
            print("\033[91mCDH SERVICE\033[0m - GRITS Ground Station")
            print("=" * 50)
            print("Ground-Based Recording of Important Telemetry Stuff")
            print("-" * 50)
            print("\nSystem Information (updates every second):\n")
            print(f"CPU Temperature: {temp_str}")
            print(f"CPU Frequency:   {freq_str}")
            print(f"CPU Voltage:     {volt_str}")
            print(f"CPU Load:        {load_str}")
            print("\n" + "-" * 50)
            print(f"Listening on {self.ip}:{self.port} for incoming packets")
            print("Press Ctrl+C to exit")
            print("=" * 50)
            
        except Exception as e:
            # Don't print errors to avoid cluttering the display
            pass

    def start(self):
        print("Starting CDHService...")
        self.running = True
        
        # Clear the console once at startup
        self.clear_console()
        
        # Draw the static UI once
        self._draw_static_ui()
        
        print(f"CDHService started, listening on {self.ip}:{self.port}")
        
        # Start the database logger if available
        try:
            # Comment out database logger start to prevent errors
            # self.database_logger.start()
            # print("Database logger started")
            pass
        except Exception as e:
            print(f"Failed to start database logger: {e}")
        
        # Track time for controlled refresh rate
        last_refresh_time = time.time()
        refresh_interval = 1.0  # Refresh display once per second
        
        while self.running:
            try:
                # Only refresh the system info at controlled intervals
                current_time = time.time()
                if current_time - last_refresh_time >= refresh_interval:
                    self._update_dynamic_values()
                    last_refresh_time = current_time
                
                # Non-blocking socket receive with short timeout
                try:
                    self.sock.settimeout(0.1)  # Short timeout for responsive UI
                    data, addr = self.sock.recvfrom(1024)
                    if data:
                        # Process the data outside the main display loop
                        self._process_packet(data, addr)
                        # Comment out InfluxDB logging to prevent errors
                        # self.log_to_influxdb(self.port, addr[1], data, addr)
                except socket.timeout:
                    # This is expected, just continue
                    pass
                except socket.error as e:
                    if not self.running:
                        break
                    # Don't break on transient socket errors
                    time.sleep(0.5)
                    continue
                    
            except KeyboardInterrupt:
                print("\nKeyboard interrupt detected")
                self.stop()
                break
            except Exception as e:
                print(f"\nUnexpected error in main loop: {e}")
                # Don't break on other errors, try to continue
                time.sleep(0.5)
            
            # Short sleep to prevent CPU hogging
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
    print("Starting CDH Service...")
    cdh_service = None
    try:
        print("Initializing CDH Service...")
        cdh_service = CDHService()
        print("Starting CDH Service main loop...")
        cdh_service.start()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected")
        pass
    except Exception as e:
        print(f"\nFailed to start CDHService: {e}")
        import traceback
        traceback.print_exc()
        pass
    finally:
        print("Cleaning up...")
        if cdh_service:
            cdh_service.stop()
        print("Done.")
