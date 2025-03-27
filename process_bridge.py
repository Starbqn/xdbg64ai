"""
Process Bridge for Memory Debugger.
Bridges between the simulated process system and real processes.
Also supports Android process integration.
"""

import os
import sys
import logging
import platform
from typing import Optional, Dict, List, Any, Union, Tuple

from real_process_connector import (
    create_process_connector, 
    RealProcessConnector,
    ProcessInfo,
    MemoryRegion
)
from process_simulator import ProcessSimulator, SimulatedProcess, Instruction, Symbol, Breakpoint

# Try to import Android connector if available
try:
    from android_process_connector import AndroidProcessConnector, is_running_on_android
    HAS_ANDROID_SUPPORT = True
except ImportError:
    HAS_ANDROID_SUPPORT = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ProcessType:
    """Enum for process types"""
    SIMULATED = "simulated"
    REAL = "real"
    ANDROID = "android"

class ProcessBridge:
    """Bridge between simulated and real processes"""
    def __init__(self, process_simulator: ProcessSimulator):
        self.process_simulator = process_simulator
        self.system = platform.system()
        
        # Try to create a real process connector
        try:
            self.real_connector = create_process_connector()
            self.has_real_connector = True
            logger.info(f"Real process connector created for {self.system}")
        except Exception as e:
            logger.warning(f"Could not create real process connector: {e}")
            self.real_connector = None
            self.has_real_connector = False
        
        # Map of real PIDs to our internal PIDs
        self.real_pid_map = {}
        
        # Current attached process type and ID
        self.current_type = None
        self.current_id = None
    
    def list_simulated_processes(self) -> List[SimulatedProcess]:
        """List all simulated processes"""
        return self.process_simulator.list_processes()
    
    def list_real_processes(self) -> List[Dict[str, Any]]:
        """List all real processes on the system"""
        if not self.has_real_connector or self.real_connector is None:
            logger.warning("Real process listing not available")
            return []
        
        try:
            process_list = []
            real_processes = self.real_connector.list_processes()
            
            for proc in real_processes:
                process_list.append({
                    "pid": proc.pid,
                    "name": proc.name,
                    "path": proc.path,
                    "type": ProcessType.REAL
                })
            
            return process_list
        except Exception as e:
            logger.error(f"Error listing real processes: {e}")
            return []
    
    def list_all_processes(self) -> List[Dict[str, Any]]:
        """List all processes (both simulated and real)"""
        # Get simulated processes
        sim_processes = []
        for proc in self.process_simulator.list_processes():
            sim_processes.append({
                "pid": proc.pid,
                "name": proc.name,
                "type": ProcessType.SIMULATED
            })
        
        # Get real processes if available
        real_processes = self.list_real_processes()
        
        # Combine the lists
        return sim_processes + real_processes
    
    def attach_to_process(self, process_id: str, process_type: str = ProcessType.SIMULATED) -> bool:
        """Attach to either a simulated or real process"""
        if process_type == ProcessType.SIMULATED:
            # Detach from any real process first
            if self.current_type == ProcessType.REAL and self.current_id:
                if self.has_real_connector and self.real_connector is not None:
                    self.real_connector.detach_from_process()
            
            # Now attach to the simulated process
            success = self.process_simulator.get_process(process_id) is not None
            if success:
                self.current_type = ProcessType.SIMULATED
                self.current_id = process_id
                logger.info(f"Attached to simulated process {process_id}")
            return success
            
        elif process_type == ProcessType.REAL:
            if not self.has_real_connector:
                logger.error("Real process connector not available")
                return False
            
            try:
                # Convert string PID to int for real processes
                real_pid = int(process_id)
                
                # Detach from any current process
                if self.current_type and self.current_id:
                    if self.current_type == ProcessType.REAL and self.has_real_connector and self.real_connector is not None:
                        self.real_connector.detach_from_process()
                
                # Attach to the real process
                if self.real_connector is not None:
                    success = self.real_connector.attach_to_process(real_pid)
                else:
                    success = False
                if success:
                    self.current_type = ProcessType.REAL
                    self.current_id = process_id
                    self.real_pid_map[process_id] = real_pid
                    logger.info(f"Attached to real process {process_id}")
                return success
                
            except Exception as e:
                logger.error(f"Error attaching to real process: {e}")
                return False
        
        else:
            logger.error(f"Unknown process type: {process_type}")
            return False
    
    def detach_from_process(self) -> bool:
        """Detach from the currently attached process"""
        if not self.current_type or not self.current_id:
            logger.warning("Not attached to any process")
            return True
        
        if self.current_type == ProcessType.REAL:
            if self.has_real_connector and self.real_connector is not None:
                success = self.real_connector.detach_from_process()
                if success:
                    self.current_type = None
                    self.current_id = None
                return success
            return False
        
        # For simulated processes, just clear the current info
        self.current_type = None
        self.current_id = None
        return True
    
    def read_memory(self, address: str, size: int = 8) -> Optional[bytes]:
        """Read raw memory from the current process"""
        if not self.current_type or not self.current_id:
            logger.error("Not attached to any process")
            return None
        
        # Convert address from string to int
        try:
            addr_int = int(address, 16) if address.startswith("0x") else int(address, 16)
        except ValueError:
            logger.error(f"Invalid address format: {address}")
            return None
        
        if self.current_type == ProcessType.SIMULATED:
            # For simulated processes, we need to convert our API
            process = self.process_simulator.get_process(self.current_id)
            if not process:
                return None
            
            # Simulated memory is stored as a dict with hex string keys
            addr_str = address if address.startswith("0x") else f"0x{addr_int:x}"
            value = process.memory.get(addr_str)
            
            if value is None:
                return None
            
            # Convert the value to bytes based on its type
            if isinstance(value, int):
                return value.to_bytes(8, byteorder='little')
            elif isinstance(value, float):
                import struct
                return struct.pack('<d', value)
            elif isinstance(value, str):
                return value.encode('utf-8')
            else:
                return str(value).encode('utf-8')
        
        elif self.current_type == ProcessType.REAL:
            if not self.has_real_connector or self.real_connector is None:
                logger.error("Real process connector not available")
                return None
            
            return self.real_connector.read_memory(addr_int, size)
        
        return None
    
    def write_memory(self, address: str, value: Any, data_type: str = "int") -> bool:
        """Write memory to the current process"""
        if not self.current_type or not self.current_id:
            logger.error("Not attached to any process")
            return False
        
        # Convert address from string to int
        try:
            addr_int = int(address, 16) if address.startswith("0x") else int(address, 16)
        except ValueError:
            logger.error(f"Invalid address format: {address}")
            return False
        
        if self.current_type == ProcessType.SIMULATED:
            # For simulated processes, we use the simulator's API
            return self.process_simulator.write_memory(self.current_id, address, value)
        
        elif self.current_type == ProcessType.REAL:
            if not self.has_real_connector:
                logger.error("Real process connector not available")
                return False
            
            # Convert the value to bytes based on data_type
            try:
                if data_type == "int":
                    value_int = int(value)
                    data = value_int.to_bytes(8, byteorder='little')
                elif data_type == "float":
                    import struct
                    value_float = float(value)
                    data = struct.pack('<d', value_float)
                elif data_type == "string":
                    data = str(value).encode('utf-8')
                else:
                    logger.error(f"Unsupported data type: {data_type}")
                    return False
                
                return self.real_connector.write_memory(addr_int, data)
            
            except Exception as e:
                logger.error(f"Error writing memory: {e}")
                return False
        
        return False
    
    def get_memory_map(self) -> Dict[str, Dict[str, Any]]:
        """Get memory map of the current process"""
        if not self.current_type or not self.current_id:
            logger.error("Not attached to any process")
            return {}
        
        if self.current_type == ProcessType.SIMULATED:
            # For simulated processes, just return the memory dict
            process = self.process_simulator.get_process(self.current_id)
            if not process:
                return {}
            
            return self.process_simulator.get_memory_map(self.current_id)
        
        elif self.current_type == ProcessType.REAL:
            if not self.has_real_connector:
                logger.error("Real process connector not available")
                return {}
            
            # For real processes, we need to get memory regions and read some sample values
            try:
                memory_regions = self.real_connector.get_memory_regions()
                memory_map = {}
                
                # Sample a few regions
                sample_count = min(len(memory_regions), 50)
                for i in range(sample_count):
                    region = memory_regions[i]
                    addr = region.base_address
                    addr_str = f"0x{addr:x}"
                    
                    # Try to read some memory
                    try:
                        data = self.real_connector.read_memory(addr, 8)
                        if data:
                            # Try to interpret the data
                            import struct
                            
                            # As int (64-bit)
                            try:
                                int_val = int.from_bytes(data[:8], byteorder='little')
                                float_val = struct.unpack('<d', data[:8])[0]
                                
                                # Try to interpret as string if it looks printable
                                str_val = "".join(chr(b) if 32 <= b < 127 else '.' for b in data)
                                
                                # Decide on a type
                                if all(32 <= b < 127 for b in data):
                                    val_type = "string"
                                    value = str_val
                                else:
                                    val_type = "int"
                                    value = int_val
                                
                                memory_map[addr_str] = {
                                    "value": value,
                                    "type": val_type,
                                    "hex": ''.join(f'{b:02x}' for b in data)
                                }
                            except:
                                pass
                    except:
                        pass
                
                return memory_map
                
            except Exception as e:
                logger.error(f"Error getting memory map: {e}")
                return {}
        
        return {}
    
    def get_memory_regions(self) -> List[Dict[str, Any]]:
        """Get memory regions of the current process"""
        if not self.current_type or not self.current_id:
            logger.error("Not attached to any process")
            return []
        
        if self.current_type == ProcessType.SIMULATED:
            # Simulated processes don't have detailed memory regions
            process = self.process_simulator.get_process(self.current_id)
            if not process:
                return []
            
            # Create a single region for the whole memory space
            return [{
                "base_address": "0x1000",
                "size": len(process.memory) * 8,
                "protection": "rwx",
                "type": "Simulated"
            }]
        
        elif self.current_type == ProcessType.REAL:
            if not self.has_real_connector:
                logger.error("Real process connector not available")
                return []
            
            try:
                regions = self.real_connector.get_memory_regions()
                return [
                    {
                        "base_address": f"0x{r.base_address:x}",
                        "size": r.size,
                        "protection": self._protection_to_string(r.protection),
                        "type": r.type,
                        "mapped_file": r.mapped_file
                    }
                    for r in regions
                ]
            except Exception as e:
                logger.error(f"Error getting memory regions: {e}")
                return []
        
        return []
    
    def _protection_to_string(self, protection: int) -> str:
        """Convert protection flags to a string"""
        if self.system == "Windows":
            from real_process_connector import MemoryProtection
            
            result = ""
            if protection & MemoryProtection.PAGE_EXECUTE:
                result += "x"
            if protection & MemoryProtection.PAGE_READONLY:
                result += "r"
            if protection & MemoryProtection.PAGE_READWRITE:
                result += "rw"
            if protection & MemoryProtection.PAGE_EXECUTE_READ:
                result += "rx"
            if protection & MemoryProtection.PAGE_EXECUTE_READWRITE:
                result += "rwx"
            
            return result or "---"
            
        elif self.system == "Linux":
            from real_process_connector import MemoryProtection
            
            result = ""
            if protection & MemoryProtection.PROT_READ:
                result += "r"
            else:
                result += "-"
                
            if protection & MemoryProtection.PROT_WRITE:
                result += "w"
            else:
                result += "-"
                
            if protection & MemoryProtection.PROT_EXEC:
                result += "x"
            else:
                result += "-"
                
            return result
        
        return "---"  # Default for unknown systems
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the current process"""
        if not self.current_type or not self.current_id:
            logger.error("Not attached to any process")
            return {}
        
        if self.current_type == ProcessType.SIMULATED:
            process = self.process_simulator.get_process(self.current_id)
            if not process:
                return {}
            
            return {
                "pid": process.pid,
                "name": process.name,
                "type": ProcessType.SIMULATED
            }
        
        elif self.current_type == ProcessType.REAL:
            if not self.has_real_connector:
                logger.error("Real process connector not available")
                return {}
            
            try:
                import psutil
                real_pid = self.real_pid_map.get(self.current_id)
                if real_pid:
                    try:
                        proc = psutil.Process(real_pid)
                        info = proc.as_dict(attrs=['pid', 'name', 'exe', 'username', 'cpu_percent'])
                        
                        return {
                            "pid": info['pid'],
                            "name": info['name'],
                            "path": info.get('exe'),
                            "username": info.get('username'),
                            "cpu_percent": info.get('cpu_percent'),
                            "type": ProcessType.REAL
                        }
                    except psutil.NoSuchProcess:
                        return {"error": "Process no longer exists"}
            except Exception as e:
                logger.error(f"Error getting process info: {e}")
                return {}
        
        return {}