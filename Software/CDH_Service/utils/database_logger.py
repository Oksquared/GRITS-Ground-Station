import time
import threading
import random
from influxdb_client import InfluxDBClient, Point, WritePrecision
import traceback

class InfluxDBLogger:
    def __init__(self, bucket="rocket_telemetry", org="OKSquared Rocketry", 
                 token="YkMZ-1FhHqgkLO1oDvisVzrasi6CEGbWHoERTXLERxO0Xw_A6Glk3VkmaRHXC6mHUmCZVf__FVQPgcK54cJIHQ==", 
                 url="http://localhost:8086", log_interval=5):
        
        self.bucket = bucket
        self.org = org
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api()
        self.log_interval = log_interval  # Time interval in seconds
        self.running = False  # Control flag for stopping the logger

    def generate_dummy_data(self):
        """Generates random dummy telemetry data."""
        return {
            "timestamp": time.time(),  # Still in seconds but will be converted before sending
            "CPU_temperature": round(random.uniform(30, 80), 2),  # Simulated temperature (30-80°C)
            "CPU_frequency": round(random.uniform(800, 3000), 2), # Simulated frequency (800-3000 MHz)
            "CPU_voltage": round(random.uniform(0.8, 1.5), 2),    # Simulated voltage (0.8-1.5V)
            "CPU_load": round(random.uniform(0, 100), 2)          # Simulated CPU load (0-100%)
        }

    def log_data(self):
        """Logs dummy telemetry data to InfluxDB at regular intervals."""
        while self.running:
            try:
                payload = self.generate_dummy_data()  # Get dummy data

                # Convert timestamp to nanoseconds
                timestamp_ns = int(payload["timestamp"] * 1e9)

                # Create a data point
                point = (
                    Point("cpu_data")
                    .tag("CPU", "raspi-5")
                    .field("temperature", payload["CPU_temperature"])
                    .field("frequency", payload["CPU_frequency"])
                    .field("voltage", payload["CPU_voltage"])
                    .field("load", payload["CPU_load"])
                    .time(timestamp_ns, WritePrecision.NS)  # Corrected timestamp precision
                )

                # Write to InfluxDB
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
                #print(f"Logged Dummy Data: {payload}")  # Print log for debugging

            except Exception as e:
                print("Error logging to InfluxDB:")
                traceback.print_exc()

            time.sleep(self.log_interval)  # Wait before next log entry

    def start(self):
        """Starts the logging process in a separate thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.log_data)
            self.thread.daemon = True  # Allow thread to close when the program exits
            self.thread.start()
            print("InfluxDB Logger started (Dummy Data Mode)...")

    def stop(self):
        """Stops the logging process."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.client.close()
        print("InfluxDB Logger stopped.")

# Run the logger if script is executed
if __name__ == "__main__":
    logger = InfluxDBLogger(log_interval=.001)  # Logs data every 10 seconds
    try:
        logger.start()
        while True:  # Keeps the main program running
            time.sleep(.02)
    except KeyboardInterrupt:
        logger.stop()
