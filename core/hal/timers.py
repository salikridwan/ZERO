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

# File: timers.py

class STM32Timer:
    def __init__(self, mode="WSL"):
        self.mode = mode
        if self.mode == "WSL":
            self.base_freq = 1_000_000_000  
            self.simulated_counter = 0
        else:
            self.base_freq = 80_000_000  
            self.timer = TIM2(period=0xFFFF, prescaler=0)
            self.timer.counter_mode = 'up'
            self.timer.start()
    def capture(self):
        if self.mode == "WSL":
            self.simulated_counter += 1
            return self.simulated_counter * (1e9 / self.base_freq)
        else:
            return (self.timer.counter * (1e9 / self.base_freq))
    def get_clock_metrics(self):
        if self.mode == "WSL":
            return {
                'jitter': 0.0,  
                'overflow_count': 0,  
                'prescaler': 0  
            }
        else:
            return {
                'jitter': self._measure_jitter(),
                'overflow_count': self.timer.overflow_count,
                'prescaler': self.timer.prescaler
            }
    def _measure_jitter(self):
        if self.mode == "WSL":
            return 0.0  
        return 0.0  
import time
class WSLSimulatedTimer:
    def __init__(self):
        self.start_time = time.time()
    def capture(self):
        return time.time() - self.start_time
    def get_clock_metrics(self):
        return {
            'jitter': 0.0,  
            'overflow_count': 0,  
            'prescaler': 0  
        }
class ESP32Timer:
    def __init__(self):
        self.start_time = time.time()
    def capture(self):
        return time.time() - self.start_time
    def get_clock_metrics(self):
        return {
            'jitter': 0.0,  
            'overflow_count': 0,  
            'prescaler': 0  
        }
class RP2040Timer:
    def __init__(self):
        self.start_time = time.time()
    def capture(self):
        return time.time() - self.start_time
    def get_clock_metrics(self):
        return {
            'jitter': 0.0,  
            'overflow_count': 0,  
            'prescaler': 0  
        }
class GenericTimer:
    def __init__(self):
        self.start_time = time.time()
    def capture(self):
        return time.time() - self.start_time
    def get_clock_metrics(self):
        return {
            'jitter': 0.0,  
            'overflow_count': 0,  
            'prescaler': 0  
        }