# Memory Debugger (x64dbg Lite)

A robust memory editor designed for detailed system process inspection and memory manipulation, with AI-powered assistance.

![Memory Debugger Screenshot](./static/img/memory_debugger.png)

## Features

- **Process Management**
  - Simulated process debugging for practice and testing
  - Real process detection and attachment (Linux, Windows, macOS)
  - Process listing with detailed information

- **Memory Operations**
  - Read/write memory in multiple formats (hex, decimal, ASCII)
  - Memory scanning for specific values
  - Undo/redo memory modifications
  - Memory region viewing and analysis

- **Debugging Tools**
  - CPU register viewing and editing
  - Breakpoint management (execution, memory access)
  - Instruction stepping
  - Symbol table support

- **AI Assistant**
  - Natural language interface for memory operations powered by Anthropic's Claude
  - Intelligent command parsing and execution
  - Contextual responses based on current debugging session
  - Find and modify memory values using simple English commands

## Requirements

- Python 3.8+
- Flask
- Anthropic API Key (for AI assistant functionality)
- Operating system-specific requirements for real process debugging:
  - Linux: ptrace permissions (may require root access)
  - Windows: Administrative privileges for some operations
  - macOS: Developer mode enabled

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/memory-debugger.git
   cd memory-debugger
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```
   python main.py
   ```

5. Access the web interface at `http://localhost:5000`

## Packaging as a Standalone Application

To build a standalone executable:

1. Install the build dependencies:
   ```
   python install_dependencies.py
   ```

2. Run the appropriate build script for your platform:
   
   **Windows**:
   ```
   build_windows.bat
   ```
   
   **macOS**:
   ```
   ./build_macos.sh
   ```
   
   **Linux**:
   ```
   ./build_linux.sh
   ```

3. The packaged application will be available in the `dist` directory
4. A ZIP archive for distribution will be available in the `releases` directory

## Usage

### Process Selection
- Navigate to the home page to see available processes
- Switch between simulated and real processes using the tabs
- Click on a process to begin debugging

### Memory Viewing and Editing
- View memory in the main table with selectable display format
- Click on a memory address to edit its value
- Use the scan feature to find specific values in memory

### Debugging Features
- Set breakpoints on specific memory addresses
- Step through code instructions
- Examine and modify CPU registers
- View symbols and their memory locations

### Using the AI Assistant
1. Click the "AI Assistant" button in the top-right of the process view
2. Type a natural language command, for example:
   - "Find the value 42 in memory"
   - "Change the value at address 0x1000 to 100"
   - "Search for the string 'password'"
3. The AI will interpret your command and perform the appropriate action
4. Results will be displayed in the response area

## Architecture

The system consists of several core components:

- **Process Simulator**: Creates and manages simulated processes for debugging practice
- **Real Process Connector**: Interfaces with actual running processes on the system
- **Process Bridge**: Provides a unified interface between simulated and real processes
- **Memory Editor**: Handles memory operations and debugging features
- **Memory AI Assistant**: Processes natural language commands for memory operations

## Security Note

This tool is designed for educational purposes and legitimate debugging tasks. When attaching to real processes:

- Be aware of security implications and legal considerations
- Only attach to processes you own or have permission to debug
- Use with caution on production systems

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is not intended for malicious use. The developers are not responsible for any misuse of this tool. Always respect privacy, security, and applicable laws when using this software.