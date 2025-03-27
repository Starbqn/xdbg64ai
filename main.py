import os
import sys
import webbrowser
import threading
import time
import logging
from dotenv import load_dotenv
from app import app

# Load environment variables from .env file if it exists
load_dotenv(verbose=True)

# Note: sys._MEIPASS is a special path added by PyInstaller at runtime.
# It will not be present during normal Python execution but only when
# running from a PyInstaller-created bundle. IDE/linters will flag it
# as an error, but it works correctly at runtime.

def open_browser():
    """Open the web browser after a short delay to ensure the server is running."""
    time.sleep(1.5)
    url = "http://localhost:5000"
    # Print instructions to console
    print("\n" + "=" * 60)
    print("Memory Debugger is running!")
    print("=" * 60)
    print(f"Access the application at: {url}")
    print("To exit: Close this window or press Ctrl+C in the terminal")
    print("=" * 60 + "\n")
    
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Failed to open browser automatically: {e}")
        print(f"Please manually navigate to {url}")

if __name__ == "__main__":
    # Check if we're running as a packaged application
    if getattr(sys, 'frozen', False):
        # We're running from a bundle
        # sys._MEIPASS is a special attribute provided by PyInstaller at runtime
        # that points to the temporary directory containing the extracted files
        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        template_folder = os.path.join(bundle_dir, 'templates')
        static_folder = os.path.join(bundle_dir, 'static')
        app.template_folder = template_folder
        app.static_folder = static_folder
        # Disable debug mode when running as an executable
        app.debug = False
        # Start browser in a separate thread (for standalone executable)
        threading.Thread(target=open_browser).start()
    else:
        # We're running in a normal Python environment
        app.debug = True
    
    try:
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        print(f"Error: {e}")
        # If running as an executable, keep console window open on error
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to exit...")
