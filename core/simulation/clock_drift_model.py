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
