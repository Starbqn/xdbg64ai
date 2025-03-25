# Installation Instructions

Follow these steps to set up the Memory Debugger application:

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Required Packages

The Memory Debugger depends on the following Python packages:

```
anthropic==0.15.0
email-validator==2.1.0
flask==3.0.0
flask-sqlalchemy==3.1.1
gunicorn==23.0.0
psutil==5.9.8
psycopg2-binary==2.9.9
requests==2.31.0
python-dotenv==1.0.0
```

## Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/memory-debugger.git
cd memory-debugger
```

2. **Create a virtual environment (optional but recommended)**

```bash
python -m venv venv
```

3. **Activate the virtual environment**

- On Windows:
  ```bash
  venv\Scripts\activate
  ```

- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. **Install dependencies**

```bash
pip install anthropic==0.15.0 email-validator==2.1.0 flask==3.0.0 flask-sqlalchemy==3.1.1 gunicorn==23.0.0 psutil==5.9.8 psycopg2-binary==2.9.9 requests==2.31.0 python-dotenv==1.0.0
```

5. **Set up environment variables**

- Create a `.env` file in the project root directory
- Add your Anthropic API key:
  ```
  ANTHROPIC_API_KEY=your_api_key_here
  ```
- You can copy `.env.example` to `.env` as a template

6. **Run the application**

```bash
python main.py
```

7. **Access the web interface**

Open your web browser and navigate to:
```
http://localhost:5000
```

## Platform-Specific Notes

### Windows
- Administrative privileges may be required for real process debugging
- Some Windows Defender settings might restrict process access

### Linux
- `ptrace` permissions are needed for real process debugging
- You might need to run as root for some operations:
  ```bash
  sudo python main.py
  ```

### macOS
- Developer mode must be enabled
- System Integrity Protection (SIP) might restrict some operations

## Troubleshooting

- If you encounter permission errors with real processes, check your OS security settings
- Ensure your Anthropic API key is valid and has sufficient quota
- For real process debugging issues, see platform-specific documentation