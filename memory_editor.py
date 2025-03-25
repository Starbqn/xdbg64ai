import logging
from typing import Dict, Any, Optional, List
from process_simulator import ProcessSimulator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MemoryEditor:
    """Class for interacting with process memory"""
    
    def __init__(self, process_simulator: ProcessSimulator):
        self.process_simulator = process_simulator
        logger.debug("Memory editor initialized")
    
    def attach_to_process(self, process_id: str) -> bool:
        """Attach to a process for memory editing"""
        process = self.process_simulator.get_process(process_id)
        if not process:
            logger.warning(f"Failed to attach to process {process_id}: Process not found")
            return False
        
        logger.debug(f"Attached to process {process_id}")
        return True
    
    def read_process_memory(self, process_id: str) -> Dict[str, Dict[str, Any]]:
        """Read all memory from a process and format it for display"""
        if not self.attach_to_process(process_id):
            return {}
        
        memory_map = self.process_simulator.get_memory_map(process_id)
        formatted_memory = {}
        
        for address, value in memory_map.items():
            # Determine the data type of the value
            if isinstance(value, int):
                data_type = "int"
                hex_value = hex(value)
            elif isinstance(value, float):
                data_type = "float"
                hex_value = "N/A"
            elif isinstance(value, str):
                data_type = "string"
                # Convert string to hex representation
                hex_value = ' '.join([hex(ord(c))[2:] for c in value])
            else:
                data_type = "unknown"
                hex_value = "N/A"
            
            formatted_memory[address] = {
                "value": value,
                "type": data_type,
                "hex": hex_value
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
                value = int(value)
            elif data_type == "float":
                value = float(value)
            elif data_type == "string":
                value = str(value)
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
