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

"""
Zero Architecture - Phase 1: Drift Measurement Core (DMC)
Optimized for WSL (Windows Subsystem for Linux)
"""

import time
import numpy as np
import csv
import signal
import logging
from datetime import datetime
import os
import platform

# Configuration
SAMPLE_INTERVAL = 0.1  # Seconds (100ms)
BUFFER_SIZE = 6000     # 10 minutes of data at 0.1s interval
LOG_DIR = "logs"
DEBUG_MODE = True
WARMUP_SAMPLES = 5     # ignore first few samples

# Create logs directory
os.makedirs(LOG_DIR, exist_ok=True)

class DriftCollector:
    def __init__(self):
        # Allow clocks to stabilize
        time.sleep(1)
        self.reference_start = time.perf_counter()
        self.monotonic_start = time.monotonic()
        self.drift_buffer = np.zeros(BUFFER_SIZE)
        self.index = 0
        self.running = True
        self.log_file = os.path.join(LOG_DIR, f"drift_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG if DEBUG_MODE else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Register exit handler
        signal.signal(signal.SIGINT, self.safe_exit)
        signal.signal(signal.SIGTERM, self.safe_exit)
        
        # Log system information
        self.log_system_info()
        
        # Create CSV logfile
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'monotonic', 'perf_counter', 'drift_ppm'])

    def log_system_info(self):
        """Log system configuration details"""
        logging.info(f"System: {platform.system()} {platform.release()}")
        logging.info(f"Processor: {platform.processor()}")
        logging.info(f"Python: {platform.python_version()}")
        logging.info(f"WSL Version: {self.get_wsl_version()}")

    def get_wsl_version(self):
        """Attempt to determine WSL version"""
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read()
                if 'microsoft' in version_info.lower():
                    return "WSL2" if "WSL2" in version_info else "WSL1"
                return "Native Linux"
        except:
            return "Unknown"

    def measure_drift(self):
        """Capture single drift measurement"""
        monotonic_current = time.monotonic() - self.monotonic_start
        perf_current = time.perf_counter() - self.reference_start
        
        # Calculate drift in parts per million
        expected = perf_current
        actual = monotonic_current
        drift_ppm = 1e6 * (actual - expected) / expected if expected > 0 else 0

        # clamp if drift explodes
        if abs(drift_ppm) > 100:
            drift_ppm = 0
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'monotonic': monotonic_current,
            'perf_counter': perf_current,
            'drift_ppm': drift_ppm
        }

    def safe_exit(self, signum, frame):
        """Handle graceful shutdown"""
        logging.info("Shutting down drift collector")
        self.running = False

    def run(self):
        """Main collection loop"""
        logging.info(f"Starting Drift Measurement Core (Interval: {SAMPLE_INTERVAL}s)")
        logging.info(f"Logging to: {self.log_file}")
        
        WARMUP_SAMPLES = 10
        sample_count = 0

        while self.running:
            start_time = time.perf_counter()
            measurement = self.measure_drift()
            sample_count += 1

            if sample_count <= WARMUP_SAMPLES:
                continue  # skip these early cursed values

            drift = measurement['drift_ppm']
            # Update circular buffer
            self.drift_buffer[self.index] = drift
            self.index = (self.index + 1) % BUFFER_SIZE
            
            # Log to CSV
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    measurement['timestamp'],
                    measurement['monotonic'],
                    measurement['perf_counter'],
                    measurement['drift_ppm']
                ])
            
            # Calculate statistics on full buffer
            if self.index == 0:
                window = self.drift_buffer
                stats = {
                    'mean': np.mean(window),
                    'std': np.std(window),
                    'min': np.min(window),
                    'max': np.max(window)
                }
                logging.debug(f"Drift Stats: μ={stats['mean']:.2f}ppm σ={stats['std']:.2f} "
                              f"Range=[{stats['min']:.2f}, {stats['max']:.2f}]")
            
            # Sleep for remaining interval
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0, SAMPLE_INTERVAL - elapsed)
            time.sleep(sleep_time)

if __name__ == "__main__":
    collector = DriftCollector()
    collector.run()
