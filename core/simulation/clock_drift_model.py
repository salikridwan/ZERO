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

import numpy as np

def generate_drift_profile(length, sampling_rate=1):
    t = np.arange(0, length, sampling_rate)

    # sinusoidal + noise + trend
    drift = (
        5 * np.sin(0.01 * t) +           # slow sine wave, amplitude in ppm
        np.random.normal(0, 0.5, len(t)) +  # white noise
        0.01 * t                         # linear drift over time
    )
    return drift  # in PPM

def apply_drift_to_clock(drift_profile, initial_time=0.0, compensation_profile=None, sampling_rate=1):
    """
    Simulate a logical clock with drift and optional compensation.
    drift_profile: array of drift values in ppm (parts per million)
    initial_time: starting logical clock value
    compensation_profile: array of compensation values to apply at each step (same length as drift_profile)
    sampling_rate: time step between samples (seconds)
    Returns: array of logical clock values over time
    """
    logical_clock = initial_time
    logical_clock_trace = []
    for i, drift_ppm in enumerate(drift_profile):
        # Apply drift
        logical_clock += sampling_rate * (1 + drift_ppm * 1e-6)
        # Apply compensation if provided
        if compensation_profile is not None:
            logical_clock += compensation_profile[i]
        logical_clock_trace.append(logical_clock)
    return np.array(logical_clock_trace)
