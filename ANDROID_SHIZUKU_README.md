# Memory Debugger with Shizuku Integration

## Overview

This version of Memory Debugger includes Shizuku integration for Android, allowing memory debugging without requiring full root access. Shizuku provides a more controlled and secure way to access process memory while maintaining most of the functionality available in the root-only version.

## What is Shizuku?

Shizuku is a tool that grants apps the ability to run commands with elevated permissions, similar to `adb shell`. It works in two modes:

1. **ADB Mode**: Works on any Android device with USB debugging enabled. Users connect their device to a computer once to set up Shizuku.
2. **Root Mode**: For rooted devices, Shizuku can start automatically without requiring a computer.

## Features Enabled by Shizuku

- List all running processes on the device
- Read memory from other app processes
- Write memory to other app processes (with limitations)
- View memory maps and regions
- All done without requiring full root access

## Requirements

- Android 8.0 (API 26) or higher
- Shizuku app installed from [Google Play](https://play.google.com/store/apps/details?id=moe.shizuku.privileged.api) or [GitHub](https://github.com/RikkaApps/Shizuku/releases)
- Either:
  - One-time USB debugging setup with a computer, or
  - A rooted device

## Setup Instructions

### Setting up Shizuku with ADB (non-rooted devices)

1. Install the Shizuku app from Google Play Store
2. Enable Developer Options on your device:
   - Go to Settings > About phone
   - Tap "Build number" 7 times
3. Enable USB debugging in Developer Options
4. Connect your device to a computer
5. Set up Shizuku by following the app's instructions
6. Once set up, you can disconnect from the computer

### Setting up Shizuku with Root

1. Install the Shizuku app from Google Play Store
2. Open the app and select "Start with root"
3. Grant root access when prompted

## Using Memory Debugger with Shizuku

1. Launch Memory Debugger
2. Select "Shizuku" as the access method
3. Tap "Check/Request Permissions"
4. Grant Shizuku permissions when prompted
5. Now you can browse processes and perform memory operations

## Limitations

- Some deeply protected system processes may still be inaccessible
- Performance may be slower than with direct root access
- On some devices, you may need to restart Shizuku after rebooting

## Troubleshooting

- If Memory Debugger can't connect to Shizuku, try restarting the Shizuku app
- If you get permission errors, make sure you've granted Shizuku permission to Memory Debugger
- On some devices, the ADB-based Shizuku may stop working after a system update, requiring reconnection to a computer

## Safety Notes

While Shizuku is safer than full root access, it still provides elevated permissions that could potentially be misused. Only use Memory Debugger on apps you own or have permission to modify.

## Building the App

See the HOW_TO_BUILD_APK.md file in the builds directory for instructions on building the app from source.
