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

def generate_drift_profile(
    length,
    sampling_rate=1,
    profile_type="slow_sine",
    sine_amplitude=5,
    sine_freq=0.01,
    noise_std=0.5,
    drift_slope=0.01,
    thermal_spikes=None,
    power_events=None,
    burst_params=None
):
    """
    Generate a drift profile with optional parameterization and event injection.
    profile_type: "slow_sine", "burst", "ramp", etc.
    thermal_spikes: list of (start_idx, duration, magnitude) tuples
    power_events: list of (idx, offset) tuples (step changes)
    burst_params: dict with keys 'start', 'duration', 'magnitude'
    """
    t = np.arange(0, length, sampling_rate)
    drift = np.zeros_like(t, dtype=float)

    if profile_type == "slow_sine":
        drift = (
            sine_amplitude * np.sin(sine_freq * t) +
            np.random.normal(0, noise_std, len(t)) +
            drift_slope * t
        )
    elif profile_type == "burst":
        drift = np.random.normal(0, noise_std, len(t)) + drift_slope * t
        if burst_params:
            start = burst_params.get("start", 0)
            duration = burst_params.get("duration", 10)
            magnitude = burst_params.get("magnitude", 20)
            end = min(start + duration, len(drift))
            drift[start:end] += magnitude
    elif profile_type == "ramp":
        drift = drift_slope * t + np.random.normal(0, noise_std, len(t))
    else:
        # Default: slow_sine
        drift = (
            sine_amplitude * np.sin(sine_freq * t) +
            np.random.normal(0, noise_std, len(t)) +
            drift_slope * t
        )

    # Inject thermal spikes
    if thermal_spikes:
        for start, duration, magnitude in thermal_spikes:
            end = min(start + duration, len(drift))
            drift[start:end] += magnitude
    # Inject power events (step changes)
    if power_events:
        for idx, offset in power_events:
            if 0 <= idx < len(drift):
                drift[idx:] += offset

    # Clamp drift to not go below -70 ppm
    drift = np.maximum(drift, -70.0)
    # Clamp stddev to < 1.0
    std = np.std(drift)
    if std > 1.0:
        mean = np.mean(drift)
        drift = mean + (drift - mean) * (1.0 / std)
    return drift  # in PPM

def apply_drift_to_clock(
    drift_profile,
    initial_time=0.0,
    compensation_profile=None,
    sampling_rate=1,
    inverse=False,
    allow_mismatch=False
):
    """
    Simulate a logical clock with drift and optional compensation.
    If inverse=True, removes drift (recovers baseline time).
    If allow_mismatch=True, compensation_profile can be shorter than drift_profile (missing values treated as 0).
    """
    logical_clock = initial_time
    logical_clock_trace = []
    n = len(drift_profile)
    comp = compensation_profile if compensation_profile is not None else None

    if comp is not None and not allow_mismatch and len(comp) != n:
        raise ValueError("compensation_profile length must match drift_profile length")

    for i, drift_ppm in enumerate(drift_profile):
        drift_factor = (1 + drift_ppm * 1e-6) if not inverse else (1 - drift_ppm * 1e-6)
        logical_clock += sampling_rate * drift_factor
        # Apply compensation if provided
        if comp is not None:
            if i < len(comp):
                logical_clock += comp[i]
            elif allow_mismatch:
                logical_clock += 0
        logical_clock_trace.append(logical_clock)
    return np.array(logical_clock_trace)
