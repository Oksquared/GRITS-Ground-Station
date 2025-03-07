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
            # Try getting frequency from /proc/cpuinfo first
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "cpu MHz" in line:
                        return float(line.split(":")[1].strip())
            
            # If that fails, try the scaling_cur_freq file
            path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
            if not os.path.exists(path):
                return -1  # File does not exist on unsupported systems
            with open(path, "r") as f:
                freq_khz = f.readline().strip()
            return float(freq_khz) / 1000.0
        except Exception as e:
            return -1

    def get_voltage(self):
        """Gets the CPU voltage or returns a default value if not available."""
        try:
            # First try vcgencmd for Raspberry Pi
            try:
                output = subprocess.check_output(["vcgencmd", "measure_volts", "core"], universal_newlines=True, timeout=1)
                if "volt=" in output:
                    voltage_mv = output.split('=')[1].strip().replace('V', '')
                    return float(voltage_mv)
            except:
                pass
            
            # If vcgencmd fails, try reading from sysfs (some systems support this)
            voltage_paths = [
                "/sys/class/power_supply/BAT0/voltage_now",
                "/sys/class/power_supply/AC/voltage_now"
            ]
            for path in voltage_paths:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        voltage_uv = int(f.read().strip())
                        return voltage_uv / 1000000.0  # Convert microvolts to volts
            
            # If all methods fail, return a default value
            return 1.2  # Default voltage
        except Exception:
            return 1.2  # Default voltage on error

    def get_cpu_load(self):
        """Reads CPU load using psutil and returns the load percentage."""
        try:
            return psutil.cpu_percent(interval=0)
        except Exception:
            try:
                # Fallback to reading from /proc/stat if psutil fails
                with open("/proc/stat", "r") as f:
                    fields = f.readline().strip().split()
                    idle = float(fields[4])
                    total = sum(float(field) for field in fields[1:])
                    return 100.0 * (1.0 - idle/total)
            except Exception:
                return 0.0

if __name__ == '__main__':
    monitor = CPUMonitor()
    print(f"Temperature: {monitor.get_temperature()}°C")
    print(f"Frequency: {monitor.get_frequency()} MHz")
    print(f"Voltage: {monitor.get_voltage()}V")
    print(f"CPU Load: {monitor.get_cpu_load()}%")
    
