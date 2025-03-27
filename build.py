"""
Build script for Memory Debugger application.
This script packages the application as a standalone executable.
"""
import os
import sys
import platform
import subprocess
import shutil

def main():
    """Build the Memory Debugger application as a standalone executable."""
    print("Building Memory Debugger application...")
    
    # Determine platform-specific details
    system = platform.system()
    if system == 'Windows':
        exe_extension = '.exe'
        icon_path = os.path.join('static', 'img', 'icon.ico')
        separator = ';'
    else:
        exe_extension = ''
        icon_path = os.path.join('static', 'img', 'icon.png')
        separator = ':'
    
    # Check if icon directories exist, create them if not
    icon_dir = os.path.join('static', 'img')
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir, exist_ok=True)
        print(f"Created icon directory: {icon_dir}")
    
    # Use the default icon if not available
    if not os.path.exists(icon_path):
        if system == 'Windows' and os.path.exists('generated-icon.png'):
            # Convert PNG to ICO for Windows
            try:
                from PIL import Image
                img = Image.open('generated-icon.png')
                icon_path = os.path.join('static', 'img', 'icon.ico')
                img.save(icon_path)
                print(f"Converted PNG icon to ICO format: {icon_path}")
            except ImportError:
                print("Warning: Pillow not installed, cannot convert PNG to ICO")
                icon_path = 'generated-icon.png'
        else:
            # Use the generated icon directly if available
            if os.path.exists('generated-icon.png'):
                icon_path = 'generated-icon.png'
                print(f"Using generated icon: {icon_path}")
    
    # Create base command
    base_cmd = [
        'pyinstaller',
        '--name=MemoryDebugger',
        '--onefile',
        '--clean',
        '--add-data=templates{}templates'.format(separator),
        '--add-data=static{}static'.format(separator),
    ]
    
    # Add icon if it exists
    if os.path.exists(icon_path):
        base_cmd.append('--icon={}'.format(icon_path))
    
    # Windows-specific options
    if system == 'Windows':
        base_cmd.append('--noconsole')
        # Add version info for Windows
        base_cmd.extend([
            '--version-file=version_info.txt',
        ])
    
    # Add main script
    base_cmd.append('main.py')
    
    # Run PyInstaller
    print("Running PyInstaller with command:", ' '.join(base_cmd))
    subprocess.run(base_cmd, check=True)
    
    # Copy additional files to dist folder
    print("Copying additional files...")
    dist_dir = os.path.join('dist')
    
    # Create .env.example in the distribution
    shutil.copy('.env.example', os.path.join(dist_dir, '.env.example'))
    
    # Copy README and license
    if os.path.exists('RELEASE_README.md'):
        # Use the release-specific README if available
        shutil.copy('RELEASE_README.md', os.path.join(dist_dir, 'README.md'))
    else:
        shutil.copy('README.md', os.path.join(dist_dir, 'README.md'))
    
    # Copy installation instructions if available
    if os.path.exists('INSTALLATION.md'):
        shutil.copy('INSTALLATION.md', os.path.join(dist_dir, 'INSTALLATION.md'))
    
    shutil.copy('LICENSE', os.path.join(dist_dir, 'LICENSE'))
    
    # Create a basic installation guide
    with open(os.path.join(dist_dir, 'INSTALL.txt'), 'w') as f:
        f.write("""MEMORY DEBUGGER INSTALLATION GUIDE
==============================

1. Extract all files to a directory of your choice.
2. Copy the .env.example file to .env and edit it to add your Anthropic API key.
3. Run the MemoryDebugger executable.
4. Access the application through your web browser at http://localhost:5000

Note: When running on Windows or macOS, you may need to grant additional permissions
for the application to access real system processes.
""")
    
    print("Build completed successfully!")
    print(f"Executable can be found in the '{dist_dir}' directory.")

if __name__ == "__main__":
    main()