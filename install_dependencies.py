#!/usr/bin/env python3
"""
Install dependencies required for building Memory Debugger.
This script ensures all required dependencies are installed before running the build scripts.
"""
import os
import sys
import subprocess
import platform

def main():
    """Install dependencies required for building Memory Debugger."""
    print("Installing dependencies for Memory Debugger...")
    
    # Determine platform-specific details
    system = platform.system()
    
    # Make sure pip is up to date
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Base dependencies
    dependencies = [
        "anthropic",
        "email-validator",
        "flask",
        "flask-sqlalchemy",
        "gunicorn",
        "psutil",
        "requests",
        "python-dotenv",
        "pyinstaller",
        "pillow"  # For icon conversion
    ]
    
    # Platform-specific dependencies
    if system == "Windows":
        dependencies.append("pywin32")
    elif system == "Linux":
        dependencies.append("psycopg2-binary")
    elif system == "Darwin":  # macOS
        dependencies.append("psycopg2-binary")
    
    # Install dependencies
    print(f"Installing the following packages: {', '.join(dependencies)}")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencies)
    
    print("\nDependencies installed successfully!")
    print("You can now run the build scripts:")
    if system == "Windows":
        print("  build_windows.bat")
    elif system == "Linux":
        print("  ./build_linux.sh")
    elif system == "Darwin":  # macOS
        print("  ./build_macos.sh")
    else:
        print("  python build.py")

if __name__ == "__main__":
    main()