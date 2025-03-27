#!/bin/bash
# Build script for the Android version of Memory Debugger with Shizuku support

echo "Building Memory Debugger for Android with Shizuku support..."
echo "============================================================"

# Make sure required directories exist
mkdir -p builds

# Run the Python build script
python3 build_android_shizuku.py

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "============================================================"
    echo "Build completed successfully!"
    echo "The Android project has been created in the android_app directory."
    echo "A placeholder APK has been created in the builds directory."
    echo ""
    echo "To build the actual APK:"
    echo "1. Open the android_app directory in Android Studio"
    echo "2. Let Gradle sync complete"
    echo "3. Build > Build Bundle(s) / APK(s) > Build APK(s)"
    echo ""
    echo "See ANDROID_SHIZUKU_README.md for more information on using Shizuku."
else
    echo "============================================================"
    echo "Build failed! Check the error messages above."
fi