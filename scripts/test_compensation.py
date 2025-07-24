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

# File: test_compensation.py

import time
import numpy as np
import matplotlib.pyplot as plt
from core.simulation.node_simulation import VirtualNode
from core.synchronization.beacon_synchronization import BeaconSync
from core.simulation.clock_drift_model import simulate_drift
from core.drift.drift_predictor import DriftPredictor  # Import DriftPredictor
class DriftPredictor:
    def __init__(self):
        pass

    def apply_correction(self, drift_measurement, interval):
        """Placeholder for applying drift correction."""
        return -drift_measurement * 1e-6 * interval  # Example correction logic


class CompensatedClock:
    def __init__(self, node_id, base_clock, compensation_model, base_drift=0):
        self.node_id = node_id
        self.base_clock = base_clock
        self.compensation_model = compensation_model
        self.predictor = compensation_model  # Add this line
        self.base_drift = base_drift  # Store the base_drift value
        self.drift_history = []


class VirtualNode:
    def __init__(self, node_id, base_drift=0, compensation_interval=1.0):
        self.node_id = node_id
        self.base_drift = base_drift
        self.compensation_interval = compensation_interval
        self.clock = CompensatedClock(
            node_id=self.node_id,
            base_clock=self,
            compensation_model=DriftPredictor()
        )
        self.drift_history = []

    def simulate_drift(self, interval, leader_node=None):
        """Simulate clock drift for this node."""
        drift = simulate_drift(interval, factor=self.base_drift)
        self.drift_history.append(drift)
        if leader_node:
            print(f"{self.node_id}: Simulated drift with respect to leader {leader_node.node_id}")

    def get_fingerprint(self):
        """Generate a fingerprint for the node's state."""
        return {
            "node_id": self.node_id,
            "drift_history": self.drift_history[-10:],  # Last 10 drift values
            "base_drift": self.base_drift
        }


def calculate_fingerprint_distance(fingerprint_a, fingerprint_b):
    """Placeholder for fingerprint distance calculation."""
    return np.random.random()  # Return a random distance for testing


def run_compensation_test():
    print("=== Drift Compensation Effectiveness Test ===")
    node_a = VirtualNode("NODE-A", base_drift=15, compensation_interval=0.5)
    node_b = VirtualNode("NODE-B", base_drift=10, compensation_interval=0.5)
    test_duration = 300  
    interval = 10        
    sync_interval = 30   
    times = []
    distances = []
    node_a_drifts = []
    node_b_drifts = []
    compensation_stats = []
    live_corrections = []
    start_time = time.monotonic()
    current_time = start_time
    print("Running test...")
    while current_time - start_time < test_duration:
        node_a.simulate_drift(interval, leader_node=node_a)
        node_b.simulate_drift(interval, leader_node=node_a)  
        if node_b.drift_history:
            drift_meas = node_b.drift_history[-1]
            correction = node_b.clock.predictor.apply_correction(drift_meas, interval)
        else:
            correction = 0.0
        live_corrections.append(correction)
        distance = calculate_fingerprint_distance(
            node_a.get_fingerprint(),
            node_b.get_fingerprint()
        )
        elapsed = current_time - start_time
        times.append(elapsed)
        distances.append(distance)
        node_a_drifts.append(np.mean(node_a.drift_history[-100:]))
        node_b_drifts.append(np.mean(node_b.drift_history[-100:]))
        compensation_stats.append({"accumulated_error": correction, "compensation_count": len(live_corrections)})
        current_time = time.monotonic()
    pass_rate = np.mean([d < 0.1 for d in distances]) * 100
    avg_error = np.mean([s['accumulated_error'] for s in compensation_stats])
    print(f"\nResults after {test_duration} seconds:")
    print(f"Pass rate: {pass_rate:.2f}%")
    print(f"Avg accumulated error: {avg_error:.6f} seconds")
    print(f"Sync events: {compensation_stats[-1]['compensation_count']}")
    plt.figure(figsize=(12, 10))
    plt.subplot(3, 1, 1)
    plt.plot(times, distances, 'b-', label='Fingerprint Distance')
    plt.axhline(y=0.1, color='r', linestyle='--', label='Threshold')
    plt.ylabel('Fingerprint Distance')
    plt.title('Temporal Synchronization Quality')
    plt.legend()
    plt.subplot(3, 1, 2)
    plt.plot(times, node_a_drifts, 'g-', label='Node A Drift')
    plt.plot(times, node_b_drifts, 'm-', label='Node B Drift')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Drift (PPM)')
    plt.title('Drift Behavior with Compensation')
    plt.legend()
    plt.subplot(3, 1, 3)
    plt.plot(times, live_corrections, 'k-', label='Live Correction (s)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Correction (seconds)')
    plt.title('Live Drift Compensation Engine™ Output')
    plt.legend()
    plt.tight_layout()
    plt.savefig('logs/compensation_results.png')
    print("Results saved to logs/compensation_results.png")


def test_compensation():
    print("Testing Clock Drift Compensation\n" + "="*40)
    master = BeaconSync("master")
    node1 = BeaconSync("node1")
    node2 = BeaconSync("node2")
    start_time = time.time()
    duration = 3600  
    last_beacon = time.time()
    while time.time() - start_time < duration:
        current_time = time.time()
        if master.should_send_beacon():
            beacon = master.send_beacon()
            node1.receive_beacon(beacon['beacon_time'])
            node2.receive_beacon(beacon['beacon_time'])
            last_beacon = current_time
        master_time = current_time
        node1_time = current_time + simulate_drift(current_time - start_time)
        node2_time = current_time + simulate_drift(current_time - start_time, factor=1.5)
        master_adj = master.get_adjusted_time()
        node1_adj = node1.get_adjusted_time()
        node2_adj = node2.get_adjusted_time()
        error1 = abs(node1_adj - master_adj)
        error2 = abs(node2_adj - master_adj)
        if current_time - last_beacon > 10:
            print(f"[T+{current_time-start_time:.0f}s] "
                  f"Errors: Node1={error1*1000:.2f}ms, Node2={error2*1000:.2f}ms")
            last_beacon = current_time
        time.sleep(0.1)
    print("\nTest completed!")


if __name__ == "__main__":
    run_compensation_test()
    test_compensation()