#!/bin/bash
# Run all probability cage examples and generate figures.
# Usage: bash run_all.sh

set -e

echo "=============================================="
echo " Beware the Cage of Probability"
echo " Running all code examples..."
echo "=============================================="
echo ""

mkdir -p figures

for f in examples/ex0*.py; do
    echo "────────────────────────────────────────────"
    echo "  Running: $f"
    echo "────────────────────────────────────────────"
    python "$f"
    echo ""
done

echo "=============================================="
echo " All examples completed!"
echo " Figures saved to figures/"
echo "=============================================="
ls -la figures/*.png
