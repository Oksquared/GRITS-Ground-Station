import socket
import struct
import logging
import time
import signal
import sys

from config.service_config import COMMS_IP, COMMS_SEND_PORT, COMMS_RECIEVE_PORT, CDH_IP, CDH_SEND_PORT, CDH_RECIEVE_PORT, UART_PORT, BAUD_RATE
from utils.network_sender import NetworkSender

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class COMMSService:
    def __init__(self, ip=COMMS_IP, port=CDH_RECIEVE_PORT):
        self.ip = ip
        self.port = port
        self.running = False
        self.dummy_data = b"dummy_data"
        self.udp_sender = NetworkSender(self.ip, self.port, from_port=COMMS_SEND_PORT)

    def start(self):
        """Start the service and send UDP packets in a loop."""
        self.running = True
        logger.info(f"COMMSService started, sending UDP packets to {self.ip}:{self.port}")

        while self.running:
            try:
                data = self.dummy_data
                if data:
                    self.udp_sender.send_data(data)
            except Exception as e:
                logger.error(f"Error sending data: {e}")

            time.sleep(0.01)

    def stop(self):
        """Stop the service and clean up resources."""
        self.running = False
        self.udp_sender.close()
        logger.info("COMMSService stopped")

# Graceful shutdown handler
comms_service = COMMSService()

def signal_handler(sig, frame):
    logger.info("Received termination signal. Shutting down...")
    comms_service.stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    try:
        comms_service.start()
    except Exception as e:
        logger.error(f"Failed to start COMMSService: {e}")
        sys.exit(1)
