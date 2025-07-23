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

from core.fingerprint.temporal_fingerprint import generate_fingerprint
from core.simulation.clock_drift_model import CompensatedClock
import numpy as np
import time
import random
import logging
from datetime import datetime
import sys
import os
import queue
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VirtualNode:
    def __init__(self, node_id, base_drift=10, noise_level=0.5, 
                 compensation_interval=1.0, sync_interval=30.0, drift_trend=0.0):
        """
        Simulate a node with:
        - base_drift: Average drift in PPM
        - noise_level: Random fluctuation magnitude
        - compensation_interval: Interval for drift compensation
        - sync_interval: Interval for synchronization with leader
        """
        self.id = node_id
        self.clock = CompensatedClock(
            base_drift=base_drift,
            noise_level=noise_level,
            compensation_interval=compensation_interval
        )
        self.sync_interval = sync_interval
        self.last_sync = time.monotonic()
        self.drift_history = []
        self.event_queue = queue.Queue()
        self.cpu_running = False
        self.drift_trend = drift_trend
        
    def simulate_drift(self, duration=10, leader_node=None):
        """Simulate time passage with compensation"""
        start = time.monotonic()
        while time.monotonic() - start < duration:
            logical_time, current_drift = self.clock.update()
            self.drift_history.append(current_drift)
            
            # Handle periodic sync
            current_time = time.monotonic()
            if leader_node and (current_time - self.last_sync > self.sync_interval):
                self.clock.sync_to_leader(leader_node.clock.logical_clock)
                self.last_sync = current_time
                
        return current_drift
    
    def get_fingerprint(self):
        return generate_fingerprint(self.drift_history)
    
    def reset(self):
        """Reset drift history for new tests"""
        self.drift_history = []
        self.clock.reset()

    def cpu_loop(self, run_time=10):
        """Fake CPU loop that processes events from the event queue."""
        self.cpu_running = True
        end_time = time.monotonic() + run_time
        while self.cpu_running and time.monotonic() < end_time:
            try:
                event = self.event_queue.get(timeout=0.1)
                self.handle_event(event)
            except queue.Empty:
                pass  # No event, idle
            # Simulate CPU doing background work
            time.sleep(0.01)
        self.cpu_running = False

    def handle_event(self, event):
        """Process a single event (placeholder logic)."""
        logging.info(f"{self.id} handling event: {event}")

    def post_event(self, event):
        """Add an event to the node's event queue."""
        self.event_queue.put(event)

def calculate_fingerprint_distance(fp1, fp2):
    """Calculate normalized Hamming distance between hex fingerprints"""
    # Convert to binary strings
    bin1 = bin(int(fp1, 16))[2:].zfill(256)
    bin2 = bin(int(fp2, 16))[2:].zfill(256)
    
    # Calculate Hamming distance
    distance = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
    return distance / 256  # Normalized distance

def validate_nodes(node1, node2, threshold=0.1):
    """Validate if nodes are synchronized within tolerance"""
    fp1 = node1.get_fingerprint()
    fp2 = node2.get_fingerprint()
    
    logging.info(f"{node1.id} Fingerprint: {fp1[:16]}...")
    logging.info(f"{node2.id} Fingerprint: {fp2[:16]}...")
    
    distance = calculate_fingerprint_distance(fp1, fp2)
    logging.info(f"Fingerprint Distance: {distance:.4f}")
    
    return distance < threshold

def simulate_network_partition(node1, node2, duration):
    """Simulate network partition where nodes drift independently"""
    logging.warning(f"⚠️ SIMULATING NETWORK PARTITION FOR {duration}s ⚠️")
    node1.simulate_drift(duration)
    node2.simulate_drift(duration)

def run_test_scenario():
    """Run comprehensive test scenario"""
    print("\n" + "="*60)
    print("Zero Architecture - Temporal Coordination Simulator")
    print("="*60)
    
    # Create nodes with different drift profiles
    node_a = VirtualNode("NODE-A", base_drift=15, noise_level=0.3, drift_trend=0.005)
    node_b = VirtualNode("NODE-B", base_drift=10, noise_level=0.4, drift_trend=0.003)
    
    # Test 1: Initial synchronization
    print("\n[TEST 1] Initial Synchronization")
    for i in range(3):
        node_a.simulate_drift(10)
        node_b.simulate_drift(10)
        result = validate_nodes(node_a, node_b)
        status = "PASS" if result else "FAIL"
        print(f"  Cycle {i+1}: {status}")

    # Test 2: Network partition recovery
    print("\n[TEST 2] Network Partition Recovery")
    simulate_network_partition(node_a, node_b, 30)  # 30-second partition
    
    # Post-partition validation
    result = validate_nodes(node_a, node_b)
    print(f"  Post-Partition: {'PASS' if result else 'FAIL'}")
    
    if not result:
        # Simulate recovery attempt
        print("  Initiating recovery protocol...")
        for i in range(3):
            node_a.simulate_drift(10)
            node_b.simulate_drift(10)
            result = validate_nodes(node_a, node_b)
            if result:
                print(f"  Recovered at cycle {i+1}")
                break
    
    # Test 3: Long-term operation
    print("\n[TEST 3] Long-term Operation (1 hour)")
    for hour in range(1, 7):  # 6 * 10-min segments = 1 hour
        for segment in range(6):  # 10 min = 6 * 100s
            node_a.simulate_drift(100)
            node_b.simulate_drift(100)
        
        result = validate_nodes(node_a, node_b)
        status = "PASS" if result else "FAIL"
        print(f"  Hour {hour}: {status}")
        if not result:
            print("  ⚠️ Degraded operation mode activated")
    
    print("\nTest sequence completed")

if __name__ == "__main__":
    run_test_scenario()
