# Memory Debugger Installation Guide

This document provides step-by-step instructions for installing and running the Memory Debugger application.

## System Requirements

- **Windows:** Windows 10 or later (64-bit)
- **macOS:** macOS 10.15 (Catalina) or later
- **Linux:** Most modern Linux distributions (Ubuntu 20.04+, Fedora 32+, etc.)

## Installation Steps

### Windows

1. Extract the ZIP file to a directory of your choice
2. Copy the `.env.example` file to `.env` in the same directory
3. Edit the `.env` file and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Double-click the `MemoryDebugger.exe` file to start the application
5. Access the application in your web browser at: http://localhost:5000

### macOS

1. Extract the ZIP file to a directory of your choice
2. Copy the `.env.example` file to `.env` in the same directory
3. Edit the `.env` file and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Open Terminal and navigate to the extracted directory
5. Make the executable file runnable:
   ```bash
   chmod +x MemoryDebugger
   ```
6. Run the application:
   ```bash
   ./MemoryDebugger
   ```
7. Access the application in your web browser at: http://localhost:5000

### Linux

1. Extract the ZIP file to a directory of your choice
2. Copy the `.env.example` file to `.env` in the same directory
3. Edit the `.env` file and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Make the executable file runnable:
   ```bash
   chmod +x MemoryDebugger
   ```
5. Run the application:
   ```bash
   ./MemoryDebugger
   ```
6. Access the application in your web browser at: http://localhost:5000

## Troubleshooting

### Windows

- If you see a security warning, click "More info" and then "Run anyway"
- To access real system processes, you may need to run the application as Administrator

### macOS

- If you see a security warning about an unidentified developer:
  1. Right-click (or Control-click) the application
  2. Select "Open" from the context menu
  3. Click "Open" in the dialog that appears
- To access real system processes, you may need to run with sudo:
  ```bash
  sudo ./MemoryDebugger
  ```

### Linux

- To access real system processes, you may need to run with sudo:
  ```bash
  sudo ./MemoryDebugger
  ```

## Getting Help

If you encounter any issues while installing or using the Memory Debugger, please:

1. Check the included README.md file for additional information
2. Visit our GitHub repository to report issues or ask questions
3. Make sure your Anthropic API key is valid and has been correctly added to the .env file

## Uninstallation

To uninstall Memory Debugger, simply delete the extracted directory and all its contents.