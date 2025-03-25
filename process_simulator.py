import uuid
import logging
import random
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SimulatedProcess:
    """Class representing a simulated process with memory"""
    
    def __init__(self, name: str, pid: str, memory: Optional[Dict[str, Any]] = None):
        self.name = name
        self.pid = pid
        self.memory = memory or {}
        
    def __str__(self):
        return f"{self.name} (PID: {self.pid})"

class ProcessSimulator:
    """Class for simulating processes that can be attached to for memory editing"""
    
    def __init__(self):
        self.processes: Dict[str, SimulatedProcess] = {}
        logger.debug("Process simulator initialized")
    
    def create_process(self, name: str, initial_memory: Optional[Dict[str, Any]] = None) -> str:
        """Create a new simulated process with given name and optional initial memory"""
        pid = str(uuid.uuid4())
        
        # If no initial memory provided, create some random values
        if initial_memory is None:
            initial_memory = {}
            base_address = random.randint(0x1000, 0x10000)
            for i in range(10):
                address = hex(base_address + (i * 4))
                # Randomly choose between int, float, and string values
                value_type = random.choice([0, 1, 2])
                if value_type == 0:
                    value = random.randint(0, 1000)
                elif value_type == 1:
                    value = round(random.uniform(0, 100), 2)
                else:
                    value = f"String_{i}"
                initial_memory[address] = value
        
        self.processes[pid] = SimulatedProcess(name, pid, initial_memory)
        logger.debug(f"Created process: {name} with PID: {pid}")
        return pid
    
    def delete_process(self, pid: str) -> bool:
        """Delete a simulated process by PID"""
        if pid in self.processes:
            del self.processes[pid]
            logger.debug(f"Deleted process with PID: {pid}")
            return True
        logger.warning(f"Attempted to delete non-existent process: {pid}")
        return False
    
    def list_processes(self) -> List[SimulatedProcess]:
        """List all simulated processes"""
        return list(self.processes.values())
    
    def get_process(self, pid: str) -> Optional[SimulatedProcess]:
        """Get a specific process by ID"""
        return self.processes.get(pid)
    
    def read_memory(self, pid: str, address: str) -> Optional[Any]:
        """Read memory at the specified address for the given process"""
        process = self.get_process(pid)
        if not process:
            logger.warning(f"Process {pid} not found")
            return None
        
        value = process.memory.get(address)
        logger.debug(f"Read memory at {address} for process {pid}: {value}")
        return value
    
    def write_memory(self, pid: str, address: str, value: Any) -> bool:
        """Write value to memory at the specified address for the given process"""
        process = self.get_process(pid)
        if not process:
            logger.warning(f"Process {pid} not found")
            return False
        
        process.memory[address] = value
        logger.debug(f"Wrote {value} to memory at {address} for process {pid}")
        return True
    
    def get_memory_map(self, pid: str) -> Dict[str, Any]:
        """Get the entire memory map for a process"""
        process = self.get_process(pid)
        if not process:
            logger.warning(f"Process {pid} not found")
            return {}
        
        return process.memory
