# Memory Debugger

A powerful tool for inspecting and manipulating process memory.

## Features

- **Process Listing**: View all running processes on your system
- **Memory Viewing**: Inspect memory contents in various formats (hex, decimal, ASCII)
- **Memory Editing**: Modify process memory values directly from the browser interface
- **Register Access**: View and modify CPU register values
- **Breakpoints**: Set, toggle, and manage breakpoints for precise control
- **AI Assistant**: Get help with memory analysis through natural language queries
- **Multi-platform Support**: Works on Windows, macOS, and Linux

## Quick Start

1. Copy the `.env.example` file to `.env` in the same directory
2. Edit the `.env` file to add your Anthropic API key (if you want to use the AI assistant feature)
3. Run the Memory Debugger executable
4. Open your web browser and go to http://localhost:5000

For more detailed instructions, please refer to the `INSTALLATION.md` file included in this package.

## Usage Notes

### Working with Simulated Processes

Simulated processes provide a safe environment to learn and practice memory debugging:

1. Click "Create New Process" to generate a simulated process
2. Click on a process name to view its memory
3. Use the interface to explore memory contents, set breakpoints, and modify values
4. The AI assistant can help answer questions about memory patterns or suggest debugging approaches

### Working with Real Processes

When working with real system processes, additional permissions may be required:

- On Windows: Run the application as Administrator
- On macOS/Linux: Run with sudo privileges

**Important**: Modifying memory in real processes can cause system instability. Use with caution.

## AI Assistant

The Memory Debugger includes an AI assistant powered by Anthropic Claude. To use this feature:

1. Obtain an API key from [Anthropic](https://www.anthropic.com/)
2. Add the key to your `.env` file as `ANTHROPIC_API_KEY=your_key_here`
3. Use the AI assistant panel to ask questions in natural language

Example questions:
- "Find the value 42 in memory"
- "What does the instruction at address 0x1000 do?"
- "Explain the memory region at 0x7FFF0000"

## Known Limitations

- Real process memory access requires elevated privileges
- Some memory regions may be protected by the operating system and cannot be accessed
- The AI assistant requires an internet connection and a valid Anthropic API key

## License

This software is distributed under the terms of the included LICENSE file.