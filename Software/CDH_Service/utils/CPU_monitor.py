#!/usr/bin/env python3

import subprocess
import psutil
import os

class CPUMonitor:
    def get_temperature(self):
        """Reads the CPU temperature from sysfs and returns it in degrees Celsius."""
        try:
            if not os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                return -1  # File does not exist on unsupported systems
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_millidegrees = f.readline().strip()
            return float(temp_millidegrees) / 1000.0
        except Exception as e:
            return -1

    def get_frequency(self):
        """Reads the CPU frequency from sysfs and returns it in MHz."""
        try:
            path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
            if not os.path.exists(path):
                return -1  # File does not exist on unsupported systems
            with open(path, "r") as f:
                freq_khz = f.readline().strip()
            return float(freq_khz) / 1000.0
        except Exception as e:
            return -1

    def get_voltage(self):
        """Reads the CPU voltage using vcgencmd and returns it in volts."""
        try:
            output = subprocess.check_output(["vcgencmd", "measure_volts", "core"], universal_newlines=True, timeout=2)
            if "volt=" not in output:
                return -1
            voltage_mv = output.split('=')[1].strip().replace('V', '')
            return float(voltage_mv)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, IndexError, ValueError):
            return -1

    def get_cpu_load(self):
        """Reads CPU load using psutil and returns the load percentage."""
        try:
            return psutil.cpu_percent(interval=0)
        except Exception:
            return 0.0

if __name__ == '__main__':
    monitor = CPUMonitor()
    
