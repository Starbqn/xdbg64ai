import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from process_simulator import ProcessSimulator
from memory_editor import MemoryEditor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Initialize our process simulator and memory editor
process_simulator = ProcessSimulator()
memory_editor = MemoryEditor(process_simulator)

# Sample processes for demonstration
process_simulator.create_process("Calculator", {"0x1000": 42, "0x1004": 3.14, "0x1008": "Hello"})
process_simulator.create_process("Notepad", {"0x2000": 100, "0x2004": 200, "0x2008": "World"})
process_simulator.create_process("Game", {"0x3000": 1000, "0x3004": 2000, "0x3008": "Player"})

@app.route('/')
def index():
    """Main page that lists available processes"""
    processes = process_simulator.list_processes()
    return render_template('index.html', processes=processes)

@app.route('/process/<process_id>')
def view_process(process_id):
    """View a specific process's memory"""
    process = process_simulator.get_process(process_id)
    if not process:
        flash(f"Process {process_id} not found", "danger")
        return redirect(url_for('index'))
    
    # Get memory map for display
    memory_map = memory_editor.read_process_memory(process_id)
    
    return render_template('process.html', process=process, memory_map=memory_map)

@app.route('/api/memory/<process_id>', methods=['GET'])
def get_memory(process_id):
    """API endpoint to get memory values"""
    try:
        memory_map = memory_editor.read_process_memory(process_id)
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

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Internal server error"), 500
