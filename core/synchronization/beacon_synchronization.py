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

# File: beacon_synchronization.py

import time
from .synchronization import TimeSynchronizer
class BeaconSync:
    def __init__(self, node_id, beacon_interval=10):
        self.synchronizer = TimeSynchronizer(node_id)
        self.beacon_interval = beacon_interval
        self.last_beacon_time = 0
        self.node_id = node_id
    def receive_beacon(self, beacon_time):
        current_time = time.time()
        processing_delay = (time.time() - current_time) / 2
        adjusted_beacon_time = beacon_time + processing_delay
        residual = self.synchronizer.synchronize(adjusted_beacon_time)
        print(f"[Node {self.node_id}] Sync: Reference={adjusted_beacon_time:.6f}, "
              f"Residual={residual:.6f}s, Next sync in {self.synchronizer.actual_sync_interval:.1f}s")
        return residual
    def get_adjusted_time(self):
        return self.synchronizer.get_corrected_time()
    def should_send_beacon(self):
        return (time.time() - self.last_beacon_time) >= self.beacon_interval
    def send_beacon(self):
        self.last_beacon_time = time.time()
        return {
            'node_id': self.node_id,
            'beacon_time': self.get_adjusted_time(),
            'sync_params': self.synchronizer.get_sync_parameters()
        }