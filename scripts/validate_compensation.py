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

# File: validate_compensation.py

import time
from core.sync import BeaconSync
from core.drift import DriftAnalyzer
def run_compensation_tests(hal, mode="WSL"):
    print(f"Starting compensation tests in {mode} mode...")
    sync_system = BeaconSync(hal)
    analyzer = DriftAnalyzer()
    test_phases = [
        {'name': 'baseline', 'duration': 3600},
        {'name': 'thermal_ramp', 'temp': (25, 85), 'duration': 1800},
        {'name': 'voltage_dip', 'voltage': 2.8, 'duration': 600},
        {'name': 'load_spike', 'cpu_load': 0.9, 'duration': 900}
    ]
    for phase in test_phases:
        print(f"\n=== Starting {phase['name']} test ===")
        sync_system.reset_stats()
        if 'temp' in phase:
            if mode == "WSL":
                print(f"Simulating thermal ramp from {phase['temp'][0]}°C to {phase['temp'][1]}°C")
            else:
                hal.chamber.ramp(*phase['temp'])
        if 'voltage' in phase:
            if mode == "WSL":
                print(f"Simulating voltage dip to {phase['voltage']}V")
            else:
                hal.power_supply.set_voltage(phase['voltage'])
        start_time = time.time()
        while time.time() - start_time < phase['duration']:
            if sync_system.should_send_beacon():
                beacon = sync_system.send_beacon()
            compensated_time = sync_system.get_adjusted_time()
            reference_time = time.time()  
            analyzer.record_sample(compensated_time, reference_time)
            if 'cpu_load' in phase:
                if mode == "WSL":
                    print(f"Simulating CPU load at {phase['cpu_load'] * 100}%")
                else:
                    hal.load_gen.generate_load(phase['cpu_load'])
            time.sleep(0.1)
        analyzer.generate_test_report(phase['name'])
    print("Compensation tests completed.")