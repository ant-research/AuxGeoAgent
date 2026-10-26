#!/bin/bash

set -e

scripts=(
    "point_generation.py"
    "reasoning.py"
    "agentic"
    "selection.py"
    "solution.py"
    "filter.py"
    "filter_minus1.py"
    "filter_minus2.py"
    "filter_failed.py"
    "trans.py"
)

for script in "${scripts[@]}"; do
    echo "Running $script"
    python "$script"
    if [ $? -eq 0 ]; then
        echo "✓ $script completed"
    else
        echo "✗ $script failed"
        exit 1
    fi
done

echo "All scripts executed successfully"