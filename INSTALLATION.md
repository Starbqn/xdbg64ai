# Memory Debugger Installation Guide

This guide provides detailed instructions for installing and running the Memory Debugger application on different platforms.

## Prerequisites

- Python 3.10 or later
- pip (Python package manager)
- Internet connection (for downloading dependencies)

## Installation Steps

### 1. Download and Extract

Download the Memory Debugger package and extract it to a folder of your choice.

### 2. Install Dependencies

Open a terminal or command prompt and navigate to the extracted folder. Install the required Python packages:

```bash
pip install anthropic email-validator flask flask-sqlalchemy gunicorn psutil psycopg2-binary requests python-dotenv
```

### 3. Configure Environment

1. Copy the `.env.example` file to a new file named `.env`:

   **Windows:**
   ```
   copy .env.example .env
   ```

   **macOS/Linux:**
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Anthropic API key (required for the AI assistant functionality).
   You can get an API key from [https://console.anthropic.com/](https://console.anthropic.com/)

### 4. Run the Application

1. Start the application:

   ```bash
   python main.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Platform-Specific Notes

### Windows

- If you encounter permission issues, try running the command prompt as Administrator.
- For easier Python management on Windows, consider using [Windows Terminal](https://aka.ms/terminal) and [Python Launcher](https://docs.python.org/3/using/windows.html#python-launcher-for-windows).

### macOS

- If you're using a Mac with Apple Silicon (M1/M2), ensure you're using a compatible version of Python.
- You might need to install command-line developer tools if prompted.

### Linux

- You may need to install additional system dependencies depending on your distribution:

  **Ubuntu/Debian:**
  ```
  sudo apt-get install python3-dev build-essential
  ```

  **Fedora:**
  ```
  sudo dnf install python3-devel gcc
  ```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you have installed all dependencies as listed in step 2.

2. **Permission Denied**: On macOS/Linux, you might need to make the script executable:
   ```
   chmod +x main.py
   ```

3. **Port Already in Use**: If port 5000 is already in use, edit the `.env` file and change the `PORT` value.

4. **AI Assistant Not Working**: Verify that you have properly set the `ANTHROPIC_API_KEY` in the `.env` file.

### Getting Help

If you encounter any issues not covered here, please refer to the [README.md](./README.md) file for more information or contact support.

## Updating

To update to a newer version:

1. Download the new version
2. Extract it to a new folder
3. Copy your `.env` file from the old installation to the new one
4. Run the application as described above

## Uninstallation

To uninstall the Memory Debugger:

1. Delete the application folder
2. Optionally, remove the installed Python packages if they're not used by other applications:
   ```
   pip uninstall anthropic email-validator flask flask-sqlalchemy gunicorn psutil requests
   ```