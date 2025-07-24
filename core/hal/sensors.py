#!/usr/bin/env python3
# ZERO ARCHITECTURE - PRE-DEVELOPMENT BENCHMARKING
# -------------------------------------------------
# THIS IS NOT PRODUCTION CODE - HARDWARE RESEARCH ONLY
#
# MIT License
#
# Copyright (c) 2025 Salik Ridwan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# WARNING: Experimental hardware interactions
# -------------------------------------------------

# File: sensors.py

class TemperatureSensor:
    def __init__(self, mcu, mode="WSL"):
        self.mcu = mcu
        self.mode = mode
        self.calibration = self._load_calibration() if self.mode == "MCU" else None
    def read(self):
        if self.mode == "WSL":
            return self._simulate_temperature()
        elif self.mcu == "STM32":
            return self._read_stm32_temp()
        elif self.mcu == "ESP32":
            return self._read_esp32_temp()
        else:
            return 25.0  
    def _read_stm32_temp(self):
        ADC1.channel = 18  
        raw = ADC1.read()
        return ((raw - self.calibration['v25']) / 
                self.calibration['avg_slope']) + 25
    def _read_esp32_temp(self):
        return 30.0  
    def _simulate_temperature(self):
        import random
        return 25.0 + random.uniform(-5.0, 5.0)  
    def _load_calibration(self):
        if self.mode == "WSL":
            return None  
        return {
            'v25': read_flash(0x1FFF7A2C),
            'avg_slope': read_flash(0x1FFF7A2E)
        }
class SimulatedTemperatureSensor:
    def __init__(self):
        self.current_temp = 25.0  
    def read(self):
        import random
        self.current_temp += random.uniform(-0.5, 0.5)
        return self.current_temp
class VoltageMonitor:
    def __init__(self, mcu=None):
        self.mcu = mcu
        self.current_voltage = 3.3  
    def read(self):
        import random
        self.current_voltage += random.uniform(-0.05, 0.05)
        return self.current_voltage
class SimulatedVoltageMonitor:
    def __init__(self):
        self.current_voltage = 3.3  
    def read(self):
        import random
        self.current_voltage += random.uniform(-0.05, 0.05)
        return self.current_voltage