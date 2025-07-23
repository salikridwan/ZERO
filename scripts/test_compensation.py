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

import time
import numpy as np
import matplotlib.pyplot as plt
from core.simulation.node_simulation import VirtualNode

def run_compensation_test():
    print("=== Drift Compensation Effectiveness Test ===")
    
    # Create nodes with different drift profiles
    node_a = VirtualNode("NODE-A", base_drift=15, compensation_interval=0.5)
    node_b = VirtualNode("NODE-B", base_drift=10, compensation_interval=0.5)
    
    # Test parameters
    test_duration = 300  # 5 minutes
    interval = 10        # Seconds between measurements
    sync_interval = 30   # Sync every 30 seconds
    
    # Data collection
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
        # Simulate with periodic sync
        node_a.simulate_drift(interval, leader_node=node_a)
        node_b.simulate_drift(interval, leader_node=node_a)  # Node A is leader

        # --- Live Drift Compensation Engine™ simulation ---
        # Get the most recent drift measurement for node_b
        if node_b.drift_history:
            drift_meas = node_b.drift_history[-1]
            # Compute live correction (in seconds) for the interval
            correction = node_b.clock.predictor.apply_correction(drift_meas, interval)
        else:
            correction = 0.0
        live_corrections.append(correction)
        # Optionally, apply this correction to a simulated logical clock here if desired

        # Validate fingerprints
        distance = calculate_fingerprint_distance(
            node_a.get_fingerprint(),
            node_b.get_fingerprint()
        )
        
        # Record data
        elapsed = current_time - start_time
        times.append(elapsed)
        distances.append(distance)
        node_a_drifts.append(np.mean(node_a.drift_history[-100:]))
        node_b_drifts.append(np.mean(node_b.drift_history[-100:]))
        compensation_stats.append(node_b.clock.get_stats())
        
        current_time = time.monotonic()
    
    # Analyze results
    pass_rate = np.mean([d < 0.1 for d in distances]) * 100
    avg_error = np.mean([s['accumulated_error'] for s in compensation_stats])
    
    print(f"\nResults after {test_duration} seconds:")
    print(f"Pass rate: {pass_rate:.2f}%")
    print(f"Avg accumulated error: {avg_error:.6f} seconds")
    print(f"Sync events: {compensation_stats[-1]['compensation_count']}")
    
    # Plot results
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
    plt.plot(times, [s['predicted_drift'] for s in compensation_stats], 
             'c--', label='Predicted Drift')
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

if __name__ == "__main__":
    run_compensation_test()