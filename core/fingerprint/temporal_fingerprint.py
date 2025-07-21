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

# fingerprint/temporal_fingerprint.py

import hashlib
import numpy as np
from scipy import stats
import struct

def generate_fingerprint(drift_data, window_size=30):
    """
    Generate a 256-bit temporal fingerprint from drift data
    using statistical features for robust identity
    """
    if isinstance(drift_data, list):
        drift_data = np.array(drift_data)
    
    samples = int(window_size * 10)
    window = drift_data[-samples:] if len(drift_data) >= samples else drift_data

    features = [
        np.mean(window),
        np.median(window),
        np.std(window),
        stats.skew(window),
        stats.kurtosis(window),
        np.max(window) - np.min(window),
        np.percentile(window, 10),
        np.percentile(window, 90)
    ]

    feature_bytes = b''.join([struct.pack('<d', f) for f in features])
    return hashlib.sha256(feature_bytes).hexdigest()
