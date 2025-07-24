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

# File: __init__.py

from .timers import STM32Timer, ESP32Timer, RP2040Timer, GenericTimer, WSLSimulatedTimer
from .sensors import TemperatureSensor, VoltageMonitor, SimulatedTemperatureSensor, SimulatedVoltageMonitor
class HardwareAbstractionLayer:
    def __init__(self, mcu_type, mode="WSL"):
        self.mcu = mcu_type
        self.mode = mode
        self.timer = self._init_timer()
        self.sensors = self._init_sensors()
    def _init_timer(self):
        if self.mode == "WSL":
            return WSLSimulatedTimer()
        elif self.mcu == "STM32":
            return STM32Timer()
        elif self.mcu == "ESP32":
            return ESP32Timer()
        elif self.mcu == "RP2040":
            return RP2040Timer()
        else:
            return GenericTimer()
    def _init_sensors(self):
        if self.mode == "WSL":
            return {
                'temp': SimulatedTemperatureSensor(),
                'voltage': SimulatedVoltageMonitor(),
                'clock_source': "Simulated"
            }
        return {
            'temp': TemperatureSensor(self.mcu),
            'voltage': VoltageMonitor(self.mcu),
            'clock_source': self._detect_clock_source()
        }
    def get_precise_time(self):
        return self.timer.capture()
    def get_environmental(self):
        return {name: sensor.read() for name, sensor in self.sensors.items()}
    def _detect_clock_source(self):
        return "Internal" if self.mcu in ("ESP32", "RP2040") else "External"