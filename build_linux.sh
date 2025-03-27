#!/bin/bash
# Linux build script for Memory Debugger
# This script builds the application and tests the packaging process

set -e  # Exit on any error

echo "=== Memory Debugger Linux Build ==="
echo "Building application..."

# Ensure build directory exists
mkdir -p builds

# Run the Python build script
python build.py

# Create the release package
python create_release.py

# Move the release to builds directory
mkdir -p builds
find releases -name "*.zip" -exec cp {} builds/ \;

echo ""
echo "=== Build Summary ==="
echo "Executable: dist/MemoryDebugger"
echo "Release package: $(find builds -name "*.zip" | head -1)"
echo ""
echo "To test the application, run:"
echo "  ./dist/MemoryDebugger"