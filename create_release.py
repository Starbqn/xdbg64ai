"""
Release script for Memory Debugger application.
This script creates release packages for different platforms.
"""
import os
import sys
import platform
import subprocess
import shutil
import zipfile
import glob
from datetime import datetime

def zip_directory(path, zip_path):
    """Zip the contents of a directory (path) into a zip file (zip_path)."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, path)
                zipf.write(file_path, arcname)

def main():
    """Create release packages for Memory Debugger application."""
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
    except:
        pass
    
    # Create release directory
    release_dir = os.path.join('releases')
    if not os.path.exists(release_dir):
        os.makedirs(release_dir)
    
    # Determine platform details
    system = platform.system()
    platform_name = system.lower()
    if platform_name == 'darwin':
        platform_name = 'macos'
    
    # Run the build script first
    print(f"Building for {system}...")
    try:
        subprocess.run([sys.executable, 'build.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return
    
    # Package the build into a zip file
    dist_dir = 'dist'
    date_str = datetime.now().strftime('%Y%m%d')
    release_filename = f"MemoryDebugger-v{version}-{platform_name}-{date_str}.zip"
    release_path = os.path.join(release_dir, release_filename)
    
    print(f"Creating release package: {release_path}")
    zip_directory(dist_dir, release_path)
    
    print("\nRelease package created successfully!")
    print(f"Package can be found at: {release_path}")
    print("\nTo create a GitHub release:")
    print("1. Go to your GitHub repository")
    print("2. Click on 'Releases'")
    print("3. Click 'Create a new release'")
    print(f"4. Set the tag to v{version}")
    print("5. Upload the generated zip file")
    print("6. Add release notes describing the changes")
    print("7. Publish the release")

if __name__ == "__main__":
    main()