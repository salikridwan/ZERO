#!/bin/bash
# TMB Validation Test Script

source .venv/bin/activate

echo "Running TMB validation tests..."

# Generate test message
python3 - <<END
from core.validation.validate_tmb import TMBValidator
from core.drift.drift_collector import DriftCollector

collector = DriftCollector()
validator = TMBValidator()

# Simulate drift collection
for _ in range(100):
    collector.measure_drift()

# Create and validate message
msg = validator.create_message(
    {"command": "activate", "params": {"duration": 1.5}},
    collector.drift_history
)
print(f"Message validation: {validator.validate_message(msg, collector.drift_history[-1])}")
END

echo "Test complete. Check data/messages for output."