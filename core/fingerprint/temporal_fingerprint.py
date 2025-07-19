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
