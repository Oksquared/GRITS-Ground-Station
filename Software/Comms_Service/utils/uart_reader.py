import serial

class UARTReader:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate)

    def read_data(self):
        if self.ser.in_waiting > 0:
            return self.ser.readline().decode('utf-8').strip()
        return None