import os
import logging
import platform
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from process_simulator import ProcessSimulator
from memory_editor import MemoryEditor, MemoryDisplay
from process_bridge import ProcessBridge, ProcessType

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Initialize our process simulator and memory editor
process_simulator = ProcessSimulator()
memory_editor = MemoryEditor(process_simulator)

# Initialize the process bridge for real process support
process_bridge = ProcessBridge(process_simulator)

# Sample processes for demonstration
process_simulator.create_process("Calculator", {"0x1000": 42, "0x1004": 3.14, "0x1008": "Hello"})
process_simulator.create_process("Notepad", {"0x2000": 100, "0x2004": 200, "0x2008": "World"})
process_simulator.create_process("Game", {"0x3000": 1000, "0x3004": 2000, "0x3008": "Player"})

@app.route('/')
def index():
    """Main page that lists available processes"""
    # Get both simulated and real processes
    simulated_processes = process_simulator.list_processes()
    
    # Try to list real processes if supported on this platform
    real_processes = process_bridge.list_real_processes()
    
    return render_template('index.html', 
                          simulated_processes=simulated_processes,
                          real_processes=real_processes,
                          system=platform.system())

@app.route('/process/<process_id>')
def view_process(process_id):
    """View a specific process's memory - simulated process"""
    process = process_simulator.get_process(process_id)
    if not process:
        flash(f"Process {process_id} not found", "danger")
        return redirect(url_for('index'))
    
    # Get memory map for display
    memory_map = memory_editor.read_process_memory(process_id)
    
    # Get code/instructions
    instructions = memory_editor.get_process_instructions(process_id)
    
    # Get registers
    registers = memory_editor.get_process_registers(process_id)
    
    # Get symbols
    symbols = memory_editor.get_symbols(process_id)
    
    # Get breakpoints
    breakpoints = memory_editor.get_breakpoints(process_id)
    
    return render_template('process.html', 
                          process=process, 
                          memory_map=memory_map, 
                          instructions=instructions,
                          registers=registers,
                          symbols=symbols,
                          breakpoints=breakpoints,
                          process_type=ProcessType.SIMULATED,
                          display_formats=[
                              MemoryDisplay.HEX,
                              MemoryDisplay.DECIMAL,
                              MemoryDisplay.ASCII,
                              MemoryDisplay.BYTES,
                              MemoryDisplay.MIXED
                          ])

@app.route('/real-process/<process_id>')
def view_real_process(process_id):
    """View a real process's memory"""
    # Try to attach to the real process
    if not process_bridge.attach_to_process(process_id, ProcessType.REAL):
        flash(f"Could not attach to real process {process_id}", "danger")
        return redirect(url_for('index'))
    
    # Get process info
    process_info = process_bridge.get_process_info()
    
    # Get memory map
    memory_map = process_bridge.get_memory_map()
    
    # Get memory regions
    memory_regions = process_bridge.get_memory_regions()
    
    return render_template('real_process.html',
                          process=process_info,
                          memory_map=memory_map,
                          memory_regions=memory_regions,
                          process_type=ProcessType.REAL,
                          system=platform.system(),
                          display_formats=[
                              MemoryDisplay.HEX,
                              MemoryDisplay.DECIMAL,
                              MemoryDisplay.ASCII,
                              MemoryDisplay.BYTES,
                              MemoryDisplay.MIXED
                          ])

@app.route('/api/memory/<process_id>', methods=['GET'])
def get_memory(process_id):
    """API endpoint to get memory values"""
    try:
        format_name = request.args.get('format')
        memory_map = memory_editor.read_process_memory(process_id, format_name)
        return jsonify({"success": True, "memory": memory_map})
    except Exception as e:
        logger.error(f"Error reading memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/memory/<process_id>', methods=['POST'])
def write_memory(process_id):
    """API endpoint to write memory values"""
    data = request.json
    address = data.get('address')
    value = data.get('value')
    data_type = data.get('type', 'int')  # Default to int
    
    if not address or value is None:
        return jsonify({"success": False, "error": "Address and value are required"}), 400
    
    try:
        memory_editor.write_process_memory(process_id, address, value, data_type)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error writing memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/memory/undo/<process_id>', methods=['POST'])
def undo_memory(process_id):
    """API endpoint to undo the last memory edit"""
    try:
        if memory_editor.undo_memory_edit(process_id):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Nothing to undo"})
    except Exception as e:
        logger.error(f"Error undoing memory edit: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/memory/redo/<process_id>', methods=['POST'])
def redo_memory(process_id):
    """API endpoint to redo a previously undone memory edit"""
    try:
        if memory_editor.redo_memory_edit(process_id):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Nothing to redo"})
    except Exception as e:
        logger.error(f"Error redoing memory edit: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/memory/scan/<process_id>', methods=['POST'])
def scan_memory(process_id):
    """API endpoint to scan memory for a value"""
    data = request.json
    value = data.get('value')
    data_type = data.get('type', 'int')  # Default to int
    
    if value is None:
        return jsonify({"success": False, "error": "Value is required"}), 400
    
    try:
        addresses = memory_editor.scan_memory(process_id, value, data_type)
        return jsonify({"success": True, "addresses": addresses})
    except Exception as e:
        logger.error(f"Error scanning memory: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/registers/<process_id>', methods=['GET'])
def get_registers(process_id):
    """API endpoint to get CPU registers"""
    try:
        registers = memory_editor.get_process_registers(process_id)
        return jsonify({"success": True, "registers": registers})
    except Exception as e:
        logger.error(f"Error getting registers: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/registers/<process_id>', methods=['POST'])
def set_register(process_id):
    """API endpoint to set a register value"""
    data = request.json
    register = data.get('register')
    value = data.get('value')
    
    if not register or value is None:
        return jsonify({"success": False, "error": "Register and value are required"}), 400
    
    try:
        if memory_editor.set_register_value(process_id, register, value):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": f"Failed to set register {register}"})
    except Exception as e:
        logger.error(f"Error setting register: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/instructions/<process_id>', methods=['GET'])
def get_instructions(process_id):
    """API endpoint to get instructions at a specific address"""
    try:
        start_address = request.args.get('address')
        count = int(request.args.get('count', 10))
        instructions = memory_editor.get_process_instructions(process_id, start_address, count)
        return jsonify({
            "success": True, 
            "instructions": [
                {
                    "address": instr.address,
                    "opcode": instr.opcode,
                    "operands": instr.operands,
                    "bytes": instr.bytes
                } for instr in instructions
            ]
        })
    except Exception as e:
        logger.error(f"Error getting instructions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/breakpoints/<process_id>', methods=['GET'])
def get_breakpoints(process_id):
    """API endpoint to get all breakpoints for a process"""
    try:
        breakpoints = memory_editor.get_breakpoints(process_id)
        return jsonify({
            "success": True, 
            "breakpoints": [
                {
                    "address": bp.address,
                    "type": bp.type,
                    "enabled": bp.enabled,
                    "condition": bp.condition,
                    "hit_count": bp.hit_count
                } for bp in breakpoints
            ]
        })
    except Exception as e:
        logger.error(f"Error getting breakpoints: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/breakpoints/<process_id>', methods=['POST'])
def set_breakpoint(process_id):
    """API endpoint to set a breakpoint"""
    data = request.json
    address = data.get('address')
    bp_type = data.get('type', 'execution')
    condition = data.get('condition')
    
    if not address:
        return jsonify({"success": False, "error": "Address is required"}), 400
    
    try:
        if memory_editor.set_breakpoint(process_id, address, bp_type, condition):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": f"Failed to set breakpoint at {address}"})
    except Exception as e:
        logger.error(f"Error setting breakpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/breakpoints/<process_id>', methods=['DELETE'])
def remove_breakpoint(process_id):
    """API endpoint to remove a breakpoint"""
    data = request.json
    address = data.get('address')
    
    if not address:
        return jsonify({"success": False, "error": "Address is required"}), 400
    
    try:
        if memory_editor.remove_breakpoint(process_id, address):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": f"Failed to remove breakpoint at {address}"})
    except Exception as e:
        logger.error(f"Error removing breakpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/breakpoints/toggle/<process_id>', methods=['POST'])
def toggle_breakpoint(process_id):
    """API endpoint to toggle a breakpoint on/off"""
    data = request.json
    address = data.get('address')
    
    if not address:
        return jsonify({"success": False, "error": "Address is required"}), 400
    
    try:
        success, new_state = memory_editor.toggle_breakpoint(process_id, address)
        if success:
            return jsonify({"success": True, "enabled": new_state})
        else:
            return jsonify({"success": False, "error": f"Failed to toggle breakpoint at {address}"})
    except Exception as e:
        logger.error(f"Error toggling breakpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/execution/step/<process_id>', methods=['POST'])
def step_instruction(process_id):
    """API endpoint to step a single instruction"""
    try:
        if memory_editor.step_instruction(process_id):
            # Get updated state
            registers = memory_editor.get_process_registers(process_id)
            instructions = memory_editor.get_process_instructions(process_id)
            return jsonify({
                "success": True, 
                "registers": registers,
                "instructions": [
                    {
                        "address": instr.address,
                        "opcode": instr.opcode,
                        "operands": instr.operands,
                        "bytes": instr.bytes
                    } for instr in instructions
                ]
            })
        else:
            return jsonify({"success": False, "error": "Failed to step instruction"})
    except Exception as e:
        logger.error(f"Error stepping instruction: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/execution/run/<process_id>', methods=['POST'])
def run_until_breakpoint(process_id):
    """API endpoint to run until a breakpoint is hit"""
    data = request.json
    max_steps = data.get('max_steps', 1000)
    
    try:
        if memory_editor.run_until_breakpoint(process_id, max_steps):
            # Get updated state
            registers = memory_editor.get_process_registers(process_id)
            instructions = memory_editor.get_process_instructions(process_id)
            return jsonify({
                "success": True, 
                "registers": registers,
                "instructions": [
                    {
                        "address": instr.address,
                        "opcode": instr.opcode,
                        "operands": instr.operands,
                        "bytes": instr.bytes
                    } for instr in instructions
                ]
            })
        else:
            return jsonify({"success": False, "error": "Failed to run process"})
    except Exception as e:
        logger.error(f"Error running process: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/symbols/<process_id>', methods=['GET'])
def get_symbols(process_id):
    """API endpoint to get all symbols for a process"""
    try:
        symbols = memory_editor.get_symbols(process_id)
        return jsonify({
            "success": True, 
            "symbols": [
                {
                    "address": sym.address,
                    "name": sym.name,
                    "type": sym.type
                } for sym in symbols
            ]
        })
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/symbols/lookup/<process_id>/<name>', methods=['GET'])
def lookup_symbol(process_id, name):
    """API endpoint to look up a symbol by name"""
    try:
        symbol = memory_editor.lookup_symbol(process_id, name)
        if symbol:
            return jsonify({
                "success": True, 
                "symbol": {
                    "address": symbol.address,
                    "name": symbol.name,
                    "type": symbol.type
                }
            })
        else:
            return jsonify({"success": False, "error": f"Symbol '{name}' not found"})
    except Exception as e:
        logger.error(f"Error looking up symbol: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/display/format', methods=['POST'])
def set_display_format():
    """API endpoint to set the memory display format"""
    data = request.json
    format_name = data.get('format')
    
    if not format_name:
        return jsonify({"success": False, "error": "Format name is required"}), 400
    
    try:
        if memory_editor.set_display_format(format_name):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": f"Invalid format: {format_name}"})
    except Exception as e:
        logger.error(f"Error setting display format: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def create_process():
    """API endpoint to create a new simulated process"""
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"success": False, "error": "Process name is required"}), 400
    
    try:
        process_id = process_simulator.create_process(name)
        return jsonify({"success": True, "process_id": process_id})
    except Exception as e:
        logger.error(f"Error creating process: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/process/<process_id>', methods=['DELETE'])
def delete_process(process_id):
    """API endpoint to delete a simulated process"""
    try:
        process_simulator.delete_process(process_id)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error deleting process: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

@app.route('/api/real-memory/<process_id>', methods=['GET'])
def get_real_memory(process_id):
    """API endpoint to get memory values from a real process"""
    try:
        if not process_bridge.attach_to_process(process_id, ProcessType.REAL):
            return jsonify({"success": False, "error": f"Could not attach to process {process_id}"}), 400
        
        memory_map = process_bridge.get_memory_map()
        
        # Detach from the process when done
        process_bridge.detach_from_process()
        
        return jsonify({"success": True, "memory": memory_map})
    except Exception as e:
        logger.error(f"Error reading real process memory: {e}")
        try:
            process_bridge.detach_from_process()
        except:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/real-memory-regions/<process_id>', methods=['GET'])
def get_real_memory_regions(process_id):
    """API endpoint to get memory regions from a real process"""
    try:
        if not process_bridge.attach_to_process(process_id, ProcessType.REAL):
            return jsonify({"success": False, "error": f"Could not attach to process {process_id}"}), 400
        
        regions = process_bridge.get_memory_regions()
        
        # Convert to JSON-serializable format
        regions_json = []
        for region in regions:
            regions_json.append({
                "base_address": region.base_address if hasattr(region, "base_address") else str(region.get("base_address", "unknown")),
                "size": region.size if hasattr(region, "size") else region.get("size", 0),
                "protection": region.protection if hasattr(region, "protection") else region.get("protection", "---"),
                "type": region.type if hasattr(region, "type") else region.get("type", "unknown"),
                "mapped_file": region.mapped_file if hasattr(region, "mapped_file") else region.get("mapped_file", "")
            })
        
        # Detach from the process when done
        process_bridge.detach_from_process()
        
        return jsonify({"success": True, "regions": regions_json})
    except Exception as e:
        logger.error(f"Error getting real process memory regions: {e}")
        try:
            process_bridge.detach_from_process()
        except:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/real-memory-view/<process_id>', methods=['GET'])
def view_real_memory(process_id):
    """API endpoint to view memory at a specific address in a real process"""
    try:
        address = request.args.get('address')
        size = int(request.args.get('size', 64))
        format_type = request.args.get('format', 'hex')
        
        if not address:
            return jsonify({"success": False, "error": "Address is required"}), 400
        
        if size <= 0 or size > 4096:
            return jsonify({"success": False, "error": "Size must be between 1 and 4096 bytes"}), 400
            
        if not process_bridge.attach_to_process(process_id, ProcessType.REAL):
            return jsonify({"success": False, "error": f"Could not attach to process {process_id}"}), 400
        
        # Convert address string to int if needed
        addr_value = int(address, 16) if address.startswith('0x') else int(address)
        
        # Read raw memory
        memory_bytes = process_bridge.read_memory(str(addr_value), size)
        
        if not memory_bytes:
            process_bridge.detach_from_process()
            return jsonify({"success": False, "error": f"Could not read memory at address {address}"}), 400
        
        # Format the memory for display based on the requested format
        memory_map = {}
        
        if format_type == 'hex':
            # Just return the raw bytes in hex format
            bytes_hex = [format(b, '02x') for b in memory_bytes]
            process_bridge.detach_from_process()
            return jsonify({"success": True, "bytes": bytes_hex})
        else:
            # Process the bytes into structured memory entries
            for i in range(0, min(len(memory_bytes), size), 8):
                if i + 8 <= len(memory_bytes):
                    chunk = memory_bytes[i:i+8]
                    addr = f"0x{(addr_value + i):x}"
                    
                    # Convert based on format
                    if format_type == 'decimal':
                        # Interpret as 64-bit integer
                        value = int.from_bytes(chunk, byteorder='little')
                        memory_map[addr] = {
                            "value": value,
                            "type": "int64",
                            "hex": ' '.join([format(b, '02x') for b in chunk])
                        }
                    elif format_type == 'ascii':
                        # Interpret as ASCII string
                        value = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in chunk])
                        memory_map[addr] = {
                            "value": value,
                            "type": "ascii",
                            "hex": ' '.join([format(b, '02x') for b in chunk])
                        }
                    else:
                        # Default to mixed format
                        int_value = int.from_bytes(chunk, byteorder='little')
                        ascii_value = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in chunk])
                        memory_map[addr] = {
                            "value": int_value,
                            "ascii": ascii_value,
                            "type": "mixed",
                            "hex": ' '.join([format(b, '02x') for b in chunk])
                        }
        
        # Detach from the process when done
        process_bridge.detach_from_process()
        
        return jsonify({"success": True, "memory": memory_map})
    except Exception as e:
        logger.error(f"Error viewing real process memory: {e}")
        try:
            process_bridge.detach_from_process()
        except:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/real-memory-write/<process_id>', methods=['POST'])
def write_real_memory(process_id):
    """API endpoint to write memory values to a real process"""
    try:
        data = request.json
        address = data.get('address')
        value = data.get('value')
        data_type = data.get('type', 'int')
        
        if not address or value is None:
            return jsonify({"success": False, "error": "Address and value are required"}), 400
            
        if not process_bridge.attach_to_process(process_id, ProcessType.REAL):
            return jsonify({"success": False, "error": f"Could not attach to process {process_id}"}), 400
        
        # Write the value to memory
        success = process_bridge.write_memory(address, value, data_type)
        
        # Detach from the process when done
        process_bridge.detach_from_process()
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": f"Failed to write to memory at {address}"}), 400
    except Exception as e:
        logger.error(f"Error writing real process memory: {e}")
        try:
            process_bridge.detach_from_process()
        except:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/processes/real', methods=['GET'])
def list_real_processes_api():
    """API endpoint to list all real processes on the system"""
    try:
        processes = process_bridge.list_real_processes()
        return jsonify({
            "success": True,
            "processes": processes
        })
    except Exception as e:
        logger.error(f"Error listing real processes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return render_template('index.html', error="Internal server error"), 500
