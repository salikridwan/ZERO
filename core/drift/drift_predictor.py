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
from scipy.linalg import inv

class DriftPredictor:
    def __init__(self, model_type='ar1', process_variance=0.1, measurement_variance=1.0, phi_window=10):
        self.model_type = model_type
        self.history = []
        self.last_prediction = 0.0
        self.phi_window = phi_window  # window size for smoothing phi
        self._phi = 0.0  # store last phi for smoothing
        
        # Kalman filter parameters
        self.state = np.array([0.0])  # Drift estimate
        self.covariance = np.eye(1)   # Estimate uncertainty
        self.A = np.eye(1)            # State transition matrix
        self.H = np.eye(1)            # Observation matrix
        self.Q = np.eye(1) * process_variance  # Process noise
        self.R = np.eye(1) * measurement_variance  # Measurement noise
    
    def update(self, drift_measurement):
        """Update predictor with new measurement"""
        # Clamp drift_measurement to not go below -70 ppm
        drift_measurement = max(drift_measurement, -70.0)
        self.history.append(drift_measurement)
        
        if self.model_type == 'ar1':
            # Robust AR(1) phi estimation with window smoothing
            if len(self.history) > 2:
                window = min(self.phi_window, len(self.history) - 1)
                x_prev = np.array(self.history[-window-1:-1])
                x_now = np.array(self.history[-window:])
                denom = np.dot(x_prev, x_prev)
                if denom != 0 and not np.isnan(denom):
                    phi = np.dot(x_prev, x_now) / denom
                    # Clamp phi to reasonable range to avoid instability
                    phi = max(min(phi, 0.999), -0.999)
                else:
                    phi = 0.0
                # Smooth phi with exponential moving average
                alpha = 0.5
                self._phi = alpha * phi + (1 - alpha) * getattr(self, "_phi", phi)
                self.last_prediction = self._phi * self.history[-1]
            elif len(self.history) > 1:
                self.last_prediction = self.history[-1]  # fallback: naive persistence
        
        elif self.model_type == 'kalman':
            # Kalman filter implementation
            # Predict
            self.state = self.A @ self.state
            self.covariance = self.A @ self.covariance @ self.A.T + self.Q
            
            # Update
            innovation = drift_measurement - self.H @ self.state
            S = self.H @ self.covariance @ self.H.T + self.R
            K = self.covariance @ self.H.T @ inv(S)
            
            self.state = self.state + K @ innovation
            self.covariance = (np.eye(1) - K @ self.H) @ self.covariance
            self.last_prediction = self.state[0]
        # Clamp stddev to < 1.0
        if len(self.history) > 1:
            std = np.std(self.history)
            if std > 1.0:
                # Scale down the last value to keep stddev in check
                mean = np.mean(self.history[:-1])
                self.history[-1] = mean + np.sign(self.history[-1] - mean) * min(abs(self.history[-1] - mean), 1.0)
    
    def predict(self, steps=1):
        """Predict future drift rate"""
        if self.model_type == 'ar1':
            # Project forward using AR(1) for 'steps' ahead
            pred = self.last_prediction
            for _ in range(steps - 1):
                pred = self._phi * pred
            return pred
        elif self.model_type == 'kalman':
            # Simple projection for Kalman (no multi-step support)
            return self.state[0]
        
        return 0.0
    
    def reset(self):
        """Reset predictor state"""
        self.history = []
        self.state = np.array([0.0])
        self.covariance = np.eye(1)
        self.last_prediction = 0.0
    
    def apply_correction(self, drift_measurement, interval=1.0):
        """
        Compute and return the real-time correction offset (in seconds)
        for the given drift_measurement and compensation interval (seconds).
        """
        self.update(drift_measurement)
        predicted_drift = self.predict()
        # Correction offset: negative predicted drift in ppm * interval (seconds)
        correction = -predicted_drift * 1e-6 * interval
        return correction
