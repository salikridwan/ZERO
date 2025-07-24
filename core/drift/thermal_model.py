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

# File: thermal_model.py

from collections import deque
class ThermalDriftModel:
    def __init__(self, clock_type, mode="WSL"):
        self.clock_type = clock_type
        self.mode = mode
        self.thermal_coeffs = self._get_coefficients()
        self.thermal_history = deque(maxlen=100)
        self.thermal_drift = 0.0  
    def compensate(self, raw_drift, env_data):
        temp = env_data.get('temp', 25.0)  
        self.thermal_history.append(temp)
        if self.mode == "WSL":
            self.thermal_drift = self._simulate_thermal_drift(temp)
        else:
            if self.clock_type == "External":
                T0 = 25  
                self.thermal_drift = self.thermal_coeffs['a'] * (temp - T0)**2
            else:
                self.thermal_drift = self.thermal_coeffs['k'] * temp
        return raw_drift - self.thermal_drift
    def _get_coefficients(self):
        if self.mode == "WSL":
            return {
                'a': -0.03,  
                'k': -0.1    
            }
        return {
            'a': -0.035,  
            'k': -0.15    
        }
    def _simulate_thermal_drift(self, temp):
        if self.clock_type == "External":
            T0 = 25  
            return -0.03 * (temp - T0)**2  
        else:
            return -0.1 * temp  
    @property
    def thermal_contribution(self):
        return self.thermal_drift
if __name__ == "__main__":
    model = ThermalDriftModel(clock_type="External", mode="WSL")
    temp_range = range(-20, 100, 10)  
    print("Testing ThermalDriftModel with External Clock:")
    for temp in temp_range:
        drift = model.compensate(raw_drift=0.0, env_data={'temp': temp})
        print(f"Temp: {temp}°C -> Compensated Drift: {drift:.5f} ppm")