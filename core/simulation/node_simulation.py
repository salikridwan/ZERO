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
import numpy as np
import time
import random
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VirtualNode:
    def __init__(self, node_id, base_drift=10, noise_level=0.5, drift_trend=0.01):
        """
        Simulate a node with:
        - base_drift: Average drift in PPM
        - noise_level: Random fluctuation magnitude
        - drift_trend: Long-term drift change per sample
        """
        self.id = node_id
        self.base_drift = base_drift
        self.noise_level = noise_level
        self.drift_trend = drift_trend
        self.drift_history = []
        self.current_drift = base_drift
        
    def simulate_drift(self, duration=10):
        """Generate simulated drift data for a duration"""
        # Simulate 10Hz sampling (10 samples per second)
        samples = int(duration * 10)
        
        for _ in range(samples):
            # Apply trend and random noise
            self.current_drift += self.drift_trend + random.gauss(0, self.noise_level)
            self.drift_history.append(self.current_drift)
        
        return self.current_drift
    
    def get_fingerprint(self):
        return generate_fingerprint(self.drift_history)
    
    def reset(self):
        """Reset drift history for new tests"""
        self.drift_history = []
        self.current_drift = self.base_drift

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
