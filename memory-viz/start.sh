#!/bin/bash
# Start the Memory Visualization Web Interface

cd "$(dirname "$0")"

echo "Starting Memory Visualization Web Interface..."
echo "Workspace: $(pwd)/.."
echo "Memory directory: $(pwd)/../memory"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Run the application
echo "Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""
python3 app.py