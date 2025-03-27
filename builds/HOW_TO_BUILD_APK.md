# How to Build the Memory Debugger APK

This is a placeholder APK file. To build the actual APK:

1. Install Android Studio from [developer.android.com](https://developer.android.com/studio)
2. Open the 'android_app' folder in Android Studio
3. Wait for Gradle sync to complete
4. Click on Build > Build Bundle(s) / APK(s) > Build APK(s)
5. The APK will be generated in 'android_app/app/build/outputs/apk/debug/'

## Requirements

- Android Studio Arctic Fox (2020.3.1) or newer
- Android SDK 30 or newer
- Android NDK 21 or newer

## Features in the Full APK

- List running processes on Android devices
- Read and write memory of processes (requires Shizuku or root)
- View memory maps of processes
- Web interface for advanced features
