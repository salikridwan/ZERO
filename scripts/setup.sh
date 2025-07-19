#!/bin/bash
# Zero Architecture - Environment Setup Script

# Configuration
VENV_DIR=".venv"
REQUIREMENTS="../requirements.txt"
DATA_DIRS=("data/drift_logs" "data/visualizations" "data/messages")

echo "Setting up Zero development environment..."

sudo apt install -y python3 python3-venv python3-pip pre-commit
# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists"
fi

# Activate and install dependencies
source $VENV_DIR/bin/activate
pip install --upgrade pip

if [ -f "$REQUIREMENTS" ]; then
    echo "Installing Python dependencies..."
    pip install -r $REQUIREMENTS
else
    echo "Error: $REQUIREMENTS not found"
    exit 1
fi

# Create data directories
for dir in "${DATA_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi
done

# Install pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Setting up pre-commit hooks..."
    pre-commit install
fi

# Generate default config if missing
if [ ! -f "config.ini" ]; then
    echo "Creating default configuration..."
    cat > config.ini <<EOL
[drift]
sample_interval = 0.1
buffer_size = 300

[tmb]
max_drift_ppm = 50
validation_window = 30

[logging]
level = INFO
EOL
fi

echo -e "\nSetup complete!\nTo activate the environment:"
echo "source $VENV_DIR/bin/activate"