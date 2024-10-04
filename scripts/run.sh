#!/bin/bash

# Check if a virtual environment exists
if [ ! -d "env" ]; then
    echo "No virtual environment found. Creating one..."
    python3 -m venv env
    source env/bin/activate
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Activating the existing virtual environment..."
    source env/bin/activate
fi

python3 main.py
