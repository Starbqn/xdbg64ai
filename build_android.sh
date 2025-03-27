#!/bin/bash
# Build script for creating Android version of Memory Debugger

echo "Memory Debugger - Android Build Script"
echo "====================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Run the Android builder script
python3 build_android.py

# Check if Android Studio is installed
if command -v studio &> /dev/null
then
    echo "Opening Android project in Android Studio..."
    studio ./android
else
    echo ""
    echo "Android Studio not found in PATH."
    echo "To complete the build process:"
    echo "1. Open Android Studio"
    echo "2. Select 'Open an existing Android Studio project'"
    echo "3. Navigate to the 'android' directory created by this script"
    echo "4. Build and run the project on your Android device"
fi

echo ""
echo "Android project setup completed!"
echo "The project is located in the 'android' directory."