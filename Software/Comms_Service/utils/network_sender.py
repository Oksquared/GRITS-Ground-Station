import socket
import struct

class NetworkSender:
    def __init__(self, ip, port, from_port=None):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Optionally bind to a fixed source port if provided.
        if from_port:
            self.sock.bind(('', from_port))
        # Cache the source port to avoid repeated getsockname() calls.
        self.source_port = self.sock.getsockname()[1]

    def send_data(self, data):
        try:
            # Build a 4-byte header with destination port and cached source port.
            header = struct.pack("!HH", self.port, self.source_port)
            # Assume data is already in raw bytes form.
            payload = header + data
            self.sock.sendto(payload, (self.ip, self.port))
        except Exception as e:
            print(f"An error occurred: {e}")

    def close(self):
        self.sock.close()