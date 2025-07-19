#!/usr/bin/env python3
"""
Zero Architecture - TMB Message Validator
Validates messages against temporal fingerprints
"""

import json
from datetime import datetime
from core.fingerprint.temporal_fingerprint import generate_fingerprint
from hashlib import sha256

class TMBValidator:
    def __init__(self, max_drift_ppm=50, window_size=30):
        self.max_drift = max_drift_ppm
        self.window = window_size
        self.drift_history = []
        
    def validate_message(self, message: dict, current_drift: float) -> bool:
        """Validate a TMB message structure"""
        required_fields = {
            'header': ['message_id', 'timestamp', 'fingerprint'],
            'body': ['payload', 'authorization']
        }
        
        # Structural validation
        for section, fields in required_fields.items():
            if section not in message:
                raise ValueError(f"Missing message section: {section}")
            for field in fields:
                if field not in message[section]:
                    raise ValueError(f"Missing field {field} in {section}")

        # Temporal validation
        return self._validate_temporal_consistency(
            message['header']['fingerprint'],
            current_drift,
            message['header']['timestamp']
        )

    def _validate_temporal_consistency(self, received_fp: str, 
                                     current_drift: float, 
                                     msg_timestamp: str) -> bool:
        """Core temporal validation logic"""
        # Update drift history
        self.drift_history.append(current_drift)
        if len(self.drift_history) > self.window * 10:  # 10Hz sampling
            self.drift_history.pop(0)

        # Generate expected fingerprint
        expected_fp = generate_fingerprint(self.drift_history)
        
        # Verify temporal consistency
        fp_match = (received_fp == expected_fp)
        
        # Verify freshness (within 2x max drift window)
        msg_time = datetime.fromisoformat(msg_timestamp)
        max_delay = (self.max_drift * 1e-6) * self.window * 2
        time_valid = (datetime.utcnow() - msg_time).total_seconds() <= max_delay
        
        return fp_match and time_valid

    @staticmethod
    def create_message(payload: dict, drift_data: list) -> dict:
        """Create a TMB-valid message structure"""
        return {
            'header': {
                'message_id': sha256(str(datetime.utcnow()).encode()).hexdigest(),
                'timestamp': datetime.utcnow().isoformat(),
                'fingerprint': generate_fingerprint(drift_data)
            },
            'body': {
                'payload': payload,
                'authorization': None  # Placeholder for auth tokens
            }
        }