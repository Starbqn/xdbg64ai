# Memory Debugger - Android Version

This document provides instructions for building and using the Android version of Memory Debugger.

## Prerequisites

1. Android Studio (latest version recommended)
2. Android SDK 24 or higher
3. Android NDK 21 or higher
4. An Android device with USB debugging enabled
5. For most memory features, a rooted Android device is required

## Building the Android Version

### Option 1: Using the build script

1. Make the build script executable:
   ```
   chmod +x build_android.sh
   ```

2. Run the build script:
   ```
   ./build_android.sh
   ```

3. Open the generated Android project in Android Studio:
   - The project will be created in the `android` directory
   - Android Studio will open automatically if it's installed

4. Build and run the app on your Android device

### Option 2: Manual setup

1. Run the Python-based Android builder:
   ```
   python build_android.py
   ```

2. Open Android Studio
3. Select "Open an existing Android Studio project"
4. Navigate to the `android` directory created by the script
5. Build and run the project

## Features and Limitations

### Features

- View list of running processes on the device
- View process memory information (requires root)
- Read memory values from processes (requires root)
- Basic memory scanning capabilities

### Limitations

- Most memory features require root access
- Writing to memory requires root and may be unstable on some devices
- Performance may be slower than the desktop version
- Not all features from the desktop version are available
- May not work on devices with strict security policies

## Troubleshooting

1. **App crashes when trying to access root**:
   - Make sure your device is rooted
   - Grant root permissions to the app when prompted
   - Some root implementations (like Magisk) may require special configuration

2. **Can't see any processes**:
   - Make sure the app has been granted the necessary permissions
   - Try restarting the app

3. **Can't access memory**:
   - Most memory operations require root access
   - Modern Android versions have additional security restrictions

4. **Build fails in Android Studio**:
   - Make sure you have the latest Android NDK installed
   - Check that CMake is properly configured in Android Studio

## Technical Details

The Android version of Memory Debugger is implemented as a native Android application with the following components:

1. **UI Layer**: Kotlin-based Android application with WebView for user interface
2. **Bridge Layer**: JavaScript to Kotlin bridge for communication
3. **Native Layer**: C++ code using JNI for memory access operations

The memory access operations use the following mechanisms:

- On rooted devices, access to `/proc/<pid>/mem` and `/proc/<pid>/maps`
- Fallback to `ptrace` for some operations where available
- On non-rooted devices, only limited information is available

## Contributing

Contributions to improve the Android version are welcome. Key areas for improvement:

1. Better error handling and reporting
2. More reliable memory access methods
3. Support for non-rooted devices (where possible)
4. Performance optimizations

## License

See the LICENSE file in the root directory for licensing information.