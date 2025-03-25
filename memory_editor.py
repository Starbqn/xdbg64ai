import logging
import binascii
from typing import Dict, Any, Optional, List, Tuple
from process_simulator import ProcessSimulator, Instruction, Breakpoint, Symbol

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MemoryDisplay:
    """Memory display format options"""
    HEX = "hex"
    DECIMAL = "decimal"
    ASCII = "ascii"
    BYTES = "bytes"
    MIXED = "mixed"

class MemoryEditor:
    """Class for interacting with process memory and debugging features"""
    
    def __init__(self, process_simulator: ProcessSimulator):
        self.process_simulator = process_simulator
        self.display_format = MemoryDisplay.MIXED
        self.current_process_id = None
        logger.debug("Memory editor initialized")
    
    def attach_to_process(self, process_id: str) -> bool:
        """Attach to a process for memory editing"""
        process = self.process_simulator.get_process(process_id)
        if not process:
            logger.warning(f"Failed to attach to process {process_id}: Process not found")
            return False
        
        self.current_process_id = process_id
        logger.debug(f"Attached to process {process_id}")
        return True
    
    def read_process_memory(self, process_id: str, display_format: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Read all memory from a process and format it for display"""
        if not self.attach_to_process(process_id):
            return {}
        
        format_to_use = display_format or self.display_format
        memory_map = self.process_simulator.get_memory_map(process_id)
        formatted_memory = {}
        
        for address, value in memory_map.items():
            # Check if there's a symbol for this address
            symbol = self.process_simulator.get_address_symbol(process_id, address)
            symbol_name = symbol.name if symbol else None
            
            # Determine the data type of the value
            if isinstance(value, int):
                data_type = "int"
                # Format based on display preference
                if format_to_use == MemoryDisplay.HEX:
                    formatted_value = hex(value)
                    hex_value = formatted_value
                elif format_to_use == MemoryDisplay.DECIMAL:
                    formatted_value = str(value)
                    hex_value = hex(value)
                elif format_to_use == MemoryDisplay.ASCII:
                    # Try to convert number to ASCII if in printable range
                    if 32 <= value <= 126:
                        formatted_value = chr(value)
                    else:
                        formatted_value = '.'  # Non-printable character
                    hex_value = hex(value)
                elif format_to_use == MemoryDisplay.BYTES:
                    # Format as bytes
                    formatted_value = f"0x{value:08x}"
                    hex_value = formatted_value
                else:  # MIXED (default)
                    formatted_value = str(value)
                    hex_value = hex(value)
            
            elif isinstance(value, float):
                data_type = "float"
                formatted_value = str(value)
                hex_value = "N/A"
            
            elif isinstance(value, str):
                data_type = "string"
                formatted_value = value
                # Convert string to hex representation
                hex_value = ' '.join([hex(ord(c))[2:] for c in value])
                
                # For ASCII format, keep the string as is
                if format_to_use == MemoryDisplay.ASCII:
                    # Replace non-printable characters with dots
                    formatted_value = ''.join([c if 32 <= ord(c) <= 126 else '.' for c in value])
            
            else:
                data_type = "unknown"
                formatted_value = str(value)
                hex_value = "N/A"
            
            # Check if there's a breakpoint at this address
            process = self.process_simulator.get_process(process_id)
            breakpoint = None
            if process:
                breakpoint = process.breakpoints.get(address)
            
            formatted_memory[address] = {
                "value": value,
                "formatted_value": formatted_value,
                "type": data_type,
                "hex": hex_value,
                "symbol": symbol_name,
                "has_breakpoint": breakpoint is not None,
                "breakpoint_enabled": breakpoint.enabled if breakpoint else False,
                "breakpoint_type": breakpoint.type if breakpoint else None
            }
        
        logger.debug(f"Read memory for process {process_id}: {len(formatted_memory)} addresses")
        return formatted_memory
    
    def write_process_memory(self, process_id: str, address: str, value: Any, data_type: str = "int") -> bool:
        """Write a value to a specific memory address"""
        if not self.attach_to_process(process_id):
            return False
        
        # Convert the value to the appropriate type
        try:
            if data_type == "int":
                # Support hex input
                if isinstance(value, str) and value.startswith('0x'):
                    value = int(value, 16)
                else:
                    value = int(value)
            elif data_type == "float":
                value = float(value)
            elif data_type == "string":
                value = str(value)
            elif data_type == "bytes":
                # Convert hex string to bytes and then to int
                if isinstance(value, str):
                    if value.startswith('0x'):
                        value = int(value, 16)
                    else:
                        # Convert space-separated hex bytes
                        value = int(''.join(value.split()), 16)
            else:
                logger.warning(f"Unknown data type: {data_type}")
                return False
        except ValueError as e:
            logger.error(f"Value conversion error: {e}")
            return False
        
        result = self.process_simulator.write_memory(process_id, address, value)
        if result:
            logger.debug(f"Wrote {value} to address {address} in process {process_id}")
        else:
            logger.warning(f"Failed to write to address {address} in process {process_id}")
        
        return result
    
    def scan_memory(self, process_id: str, value: Any, data_type: str = "int") -> List[str]:
        """Scan process memory for occurrences of a specific value"""
        if not self.attach_to_process(process_id):
            return []
        
        memory_map = self.process_simulator.get_memory_map(process_id)
        matching_addresses = []
        
        # Convert the value to the appropriate type
        try:
            if data_type == "int":
                if isinstance(value, str) and value.startswith('0x'):
                    search_value = int(value, 16)
                else:
                    search_value = int(value)
            elif data_type == "float":
                search_value = float(value)
            elif data_type == "string":
                search_value = str(value)
            else:
                logger.warning(f"Unknown data type: {data_type}")
                return []
        except ValueError as e:
            logger.error(f"Value conversion error: {e}")
            return []
        
        for address, mem_value in memory_map.items():
            if mem_value == search_value:
                matching_addresses.append(address)
        
        logger.debug(f"Found {len(matching_addresses)} matches for value {value} in process {process_id}")
        return matching_addresses
    
    def get_process_registers(self, process_id: str) -> Dict[str, int]:
        """Get the CPU registers for a process"""
        if not self.attach_to_process(process_id):
            return {}
        
        return self.process_simulator.get_registers(process_id)
    
    def set_register_value(self, process_id: str, register: str, value: Any) -> bool:
        """Set a CPU register to a specific value"""
        if not self.attach_to_process(process_id):
            return False
        
        try:
            # Support hex input
            if isinstance(value, str) and value.startswith('0x'):
                value = int(value, 16)
            else:
                value = int(value)
        except ValueError as e:
            logger.error(f"Register value conversion error: {e}")
            return False
        
        return self.process_simulator.set_register(process_id, register, value)
    
    def get_process_instructions(self, process_id: str, start_address: Optional[str] = None, count: int = 10) -> List[Instruction]:
        """Get a list of instructions from the process"""
        if not self.attach_to_process(process_id):
            return []
        
        return self.process_simulator.get_instructions(process_id, start_address, count)
    
    def set_breakpoint(self, process_id: str, address: str, bp_type: str = "execution", condition: Optional[str] = None) -> bool:
        """Set a breakpoint at the specified address"""
        if not self.attach_to_process(process_id):
            return False
        
        return self.process_simulator.set_breakpoint(process_id, address, bp_type, condition)
    
    def remove_breakpoint(self, process_id: str, address: str) -> bool:
        """Remove a breakpoint at the specified address"""
        if not self.attach_to_process(process_id):
            return False
        
        return self.process_simulator.remove_breakpoint(process_id, address)
    
    def toggle_breakpoint(self, process_id: str, address: str) -> Tuple[bool, bool]:
        """Toggle a breakpoint on/off, returns (success, new_state)"""
        if not self.attach_to_process(process_id):
            return False, False
        
        return self.process_simulator.toggle_breakpoint(process_id, address)
    
    def get_breakpoints(self, process_id: str) -> List[Breakpoint]:
        """Get all breakpoints for a process"""
        if not self.attach_to_process(process_id):
            return []
        
        return self.process_simulator.get_breakpoints(process_id)
    
    def get_symbols(self, process_id: str) -> List[Symbol]:
        """Get all symbols for a process"""
        if not self.attach_to_process(process_id):
            return []
        
        return self.process_simulator.get_symbols(process_id)
    
    def lookup_symbol(self, process_id: str, name: str) -> Optional[Symbol]:
        """Look up a symbol by name"""
        if not self.attach_to_process(process_id):
            return None
        
        return self.process_simulator.lookup_symbol(process_id, name)
    
    def step_instruction(self, process_id: str) -> bool:
        """Step a single instruction in the process"""
        if not self.attach_to_process(process_id):
            return False
        
        return self.process_simulator.step_instruction(process_id)
    
    def run_until_breakpoint(self, process_id: str, max_steps: int = 1000) -> bool:
        """Run the process until a breakpoint is hit or max_steps is reached"""
        if not self.attach_to_process(process_id):
            return False
        
        return self.process_simulator.run_until_breakpoint(process_id, max_steps)
    
    def undo_memory_edit(self, process_id: str) -> bool:
        """Undo the last memory edit"""
        if not self.attach_to_process(process_id):
            return False
        
        return self.process_simulator.undo_memory_edit(process_id)
    
    def redo_memory_edit(self, process_id: str) -> bool:
        """Redo a previously undone memory edit"""
        if not self.attach_to_process(process_id):
            return False
        
        return self.process_simulator.redo_memory_edit(process_id)
    
    def set_display_format(self, format_name: str) -> bool:
        """Set the memory display format"""
        if format_name in [MemoryDisplay.HEX, MemoryDisplay.DECIMAL, MemoryDisplay.ASCII, 
                          MemoryDisplay.BYTES, MemoryDisplay.MIXED]:
            self.display_format = format_name
            return True
        return False
