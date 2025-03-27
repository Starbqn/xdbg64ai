#!/usr/bin/env python3
"""
Build script for Memory Debugger (Replit version)
This script creates packages for distribution directly from Replit
"""
import os
import sys
import platform
import shutil
import zipfile
from datetime import datetime

def zip_directory(path, zip_path):
    """Zip the contents of a directory (path) into a zip file (zip_path)."""
    print(f"Creating zip archive: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, path)
                zipf.write(file_path, arcname)

def main():
    """Create a Memory Debugger package for distribution."""
    print("=== Memory Debugger Package Builder (Replit Version) ===")
    
    # Create output directories
    build_dir = os.path.join('builds')
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Get current version from version_info.txt or set default
    version = "1.0.0"
    try:
        with open('version_info.txt', 'r') as f:
            content = f.read()
            version_search = content.find("filevers=(")
            if version_search != -1:
                version_part = content[version_search:content.find(")", version_search)]
                version_nums = [s for s in version_part.split(',') if s.strip().isdigit()]
                if len(version_nums) >= 3:
                    version = '.'.join(version_nums[:3])
    except Exception as e:
        print(f"Warning: Could not read version info: {e}")
    
    # Create a temporary directory for the files
    temp_dir = os.path.join(build_dir, 'package')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # List of files to include
    source_files = [
        'app.py',
        'main.py',
        'memory_ai_assistant.py',
        'memory_editor.py',
        'process_bridge.py',
        'process_simulator.py',
        'real_process_connector.py',
        '.env.example',
        'INSTALLATION.md',
        'LICENSE',
        'README.md',
        'RELEASE_README.md',
        'version_info.txt',
        'requirements.txt'
    ]
    
    # Copy all Python files and supporting files
    print("Copying source files...")
    for file in source_files:
        if os.path.exists(file):
            shutil.copy(file, os.path.join(temp_dir, file))
    
    # Copy entire directories
    directories = ['templates', 'static']
    for directory in directories:
        if os.path.exists(directory):
            shutil.copytree(directory, os.path.join(temp_dir, directory))
    
    # Create a requirements.txt file if it doesn't exist
    if not os.path.exists('requirements.txt'):
        with open(os.path.join(temp_dir, 'requirements.txt'), 'w') as f:
            f.write("""anthropic>=0.49.0
email-validator>=2.2.0
flask>=3.1.0
flask-sqlalchemy>=3.1.1
gunicorn>=23.0.0
psutil>=7.0.0
requests>=2.32.3
python-dotenv>=1.0.0
""")
    
    # Create the quick start guide
    with open(os.path.join(temp_dir, 'QUICK_START.txt'), 'w') as f:
        f.write("""MEMORY DEBUGGER QUICK START GUIDE
==============================

1. Install Python 3.10 or later if you don't have it already
2. Install the required dependencies:
   pip install -r requirements.txt
3. Copy the .env.example file to .env and edit it to add your Anthropic API key
4. Run the application:
   python main.py
5. Open your web browser and go to http://localhost:5000

For more detailed instructions, see INSTALLATION.md and README.md
""")
    
    # Create the zip file
    date_str = datetime.now().strftime('%Y%m%d')
    zip_filename = f"MemoryDebugger-v{version}-source-{date_str}.zip"
    zip_path = os.path.join(build_dir, zip_filename)
    
    # Create the zip archive
    zip_directory(temp_dir, zip_path)
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    print("\n=== Package Creation Complete ===")
    print(f"Package created: {zip_path}")
    print("\nTo distribute this package:")
    print("1. Download the zip file from the Replit 'Files' panel")
    print("2. Share the zip file with your users")
    print("3. Users can extract the zip and follow the instructions in QUICK_START.txt")

if __name__ == "__main__":
    main()