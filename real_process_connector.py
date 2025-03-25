"""
Real Process Connector for Memory Debugger.
Provides functionality to attach to real running processes and manipulate their memory.
Platform-specific implementations for Windows, Linux, and macOS.
"""

import os
import sys
import logging
import platform
import subprocess
import ctypes
from typing import Optional, Dict, List, Any, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ProcessAccess:
    """Process access rights constants"""
    # Windows-specific
    PROCESS_ALL_ACCESS = 0x1F0FFF
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020
    PROCESS_VM_OPERATION = 0x0008
    
    # Linux/macOS use different mechanisms through ptrace

class MemoryProtection:
    """Memory protection constants"""
    # Windows-specific
    PAGE_EXECUTE = 0x10
    PAGE_EXECUTE_READ = 0x20
    PAGE_EXECUTE_READWRITE = 0x40
    PAGE_READONLY = 0x02
    PAGE_READWRITE = 0x04
    
    # Linux-specific
    PROT_READ = 0x1
    PROT_WRITE = 0x2
    PROT_EXEC = 0x4

class ProcessInfo:
    """Basic information about a process"""
    def __init__(self, pid: int, name: str, path: Optional[str] = None):
        self.pid = pid
        self.name = name
        self.path = path
    
    def __str__(self) -> str:
        return f"Process(pid={self.pid}, name='{self.name}')"

class MemoryRegion:
    """Represents a memory region in a process"""
    def __init__(self, base_address: int, size: int, protection: int, 
                 type_str: str, mapped_file: Optional[str] = None):
        self.base_address = base_address
        self.size = size
        self.protection = protection
        self.type = type_str
        self.mapped_file = mapped_file
    
    def __str__(self) -> str:
        base_hex = hex(self.base_address)
        return f"MemoryRegion(base={base_hex}, size={self.size}, protection={hex(self.protection)})"
    
    @property
    def end_address(self) -> int:
        """Calculate the end address of this region"""
        return self.base_address + self.size

class RealProcessConnector:
    """Base class for platform-specific process connectors"""
    def __init__(self):
        self.system = platform.system()
        self.attached_pid = None
        self.process_handle = None
        
        logger.info(f"Initializing process connector for {self.system}")
    
    def list_processes(self) -> List[ProcessInfo]:
        """List running processes on the system"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def attach_to_process(self, pid: int) -> bool:
        """Attach to a running process by PID"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def detach_from_process(self) -> bool:
        """Detach from the currently attached process"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from the attached process"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def write_memory(self, address: int, data: bytes) -> bool:
        """Write memory to the attached process"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_memory_regions(self) -> List[MemoryRegion]:
        """Get memory regions of the attached process"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def _check_attached(self) -> bool:
        """Check if we're attached to a process"""
        if self.attached_pid is None or self.process_handle is None:
            logger.error("Not attached to any process")
            return False
        return True

class WindowsProcessConnector(RealProcessConnector):
    """Windows-specific implementation using Win32 API"""
    def __init__(self):
        super().__init__()
        if self.system != "Windows":
            raise RuntimeError("WindowsProcessConnector can only be used on Windows")
        
        # Import Windows-specific modules
        try:
            import win32process
            import win32api
            import win32con
            import win32security
            import psutil
            self.win32process = win32process
            self.win32api = win32api
            self.win32con = win32con
            self.win32security = win32security
            self.psutil = psutil
            self.has_modules = True
        except ImportError:
            logger.warning("Windows modules not available. Limited functionality.")
            self.has_modules = False
    
    def list_processes(self) -> List[ProcessInfo]:
        """List running processes on Windows"""
        if not self.has_modules:
            return []
        
        processes = []
        for proc in self.psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_info = ProcessInfo(
                    pid=proc.info['pid'],
                    name=proc.info['name'],
                    path=proc.info['exe']
                )
                processes.append(process_info)
            except (self.psutil.NoSuchProcess, self.psutil.AccessDenied, KeyError):
                pass
        
        return processes
    
    def attach_to_process(self, pid: int) -> bool:
        """Attach to a running process on Windows"""
        if not self.has_modules:
            logger.error("Windows modules not available")
            return False
        
        try:
            # Get process handle with necessary access rights
            access_rights = (ProcessAccess.PROCESS_VM_READ | 
                            ProcessAccess.PROCESS_VM_WRITE | 
                            ProcessAccess.PROCESS_VM_OPERATION)
            
            process_handle = self.win32api.OpenProcess(access_rights, False, pid)
            if not process_handle:
                logger.error(f"Failed to open process {pid}")
                return False
            
            self.process_handle = process_handle
            self.attached_pid = pid
            logger.info(f"Successfully attached to process {pid}")
            return True
        
        except Exception as e:
            logger.error(f"Error attaching to process: {e}")
            return False
    
    def detach_from_process(self) -> bool:
        """Detach from the currently attached process on Windows"""
        if not self._check_attached():
            return False
        
        try:
            self.win32api.CloseHandle(self.process_handle)
            self.process_handle = None
            self.attached_pid = None
            logger.info("Successfully detached from process")
            return True
        
        except Exception as e:
            logger.error(f"Error detaching from process: {e}")
            return False
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from the attached process on Windows"""
        if not self._check_attached():
            return None
        
        try:
            # Use kernel32.dll for memory reading
            kernel32 = ctypes.windll.kernel32
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t(0)
            
            result = kernel32.ReadProcessMemory(
                int(self.process_handle), 
                ctypes.c_void_p(address), 
                buffer, 
                size, 
                ctypes.byref(bytes_read)
            )
            
            if result == 0:
                error_code = kernel32.GetLastError()
                logger.error(f"Failed to read memory at {hex(address)}, error code: {error_code}")
                return None
            
            return buffer.raw
        
        except Exception as e:
            logger.error(f"Error reading memory: {e}")
            return None
    
    def write_memory(self, address: int, data: bytes) -> bool:
        """Write memory to the attached process on Windows"""
        if not self._check_attached():
            return False
        
        try:
            # Use kernel32.dll for memory writing
            kernel32 = ctypes.windll.kernel32
            size = len(data)
            buffer = ctypes.create_string_buffer(data)
            bytes_written = ctypes.c_size_t(0)
            
            result = kernel32.WriteProcessMemory(
                int(self.process_handle), 
                ctypes.c_void_p(address), 
                buffer, 
                size, 
                ctypes.byref(bytes_written)
            )
            
            if result == 0:
                error_code = kernel32.GetLastError()
                logger.error(f"Failed to write memory at {hex(address)}, error code: {error_code}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error writing memory: {e}")
            return False
    
    def get_memory_regions(self) -> List[MemoryRegion]:
        """Get memory regions of the attached process on Windows"""
        if not self._check_attached():
            return []
        
        memory_regions = []
        
        try:
            # Use VirtualQueryEx to enumerate memory regions
            kernel32 = ctypes.windll.kernel32
            
            class MEMORY_BASIC_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("BaseAddress", ctypes.c_void_p),
                    ("AllocationBase", ctypes.c_void_p),
                    ("AllocationProtect", ctypes.c_ulong),
                    ("RegionSize", ctypes.c_size_t),
                    ("State", ctypes.c_ulong),
                    ("Protect", ctypes.c_ulong),
                    ("Type", ctypes.c_ulong)
                ]
            
            mbi = MEMORY_BASIC_INFORMATION()
            address = 0
            
            while True:
                result = kernel32.VirtualQueryEx(
                    int(self.process_handle),
                    ctypes.c_void_p(address),
                    ctypes.byref(mbi),
                    ctypes.sizeof(mbi)
                )
                
                if result == 0:
                    break
                
                # Determine memory type
                if mbi.State != 0x1000:  # MEM_COMMIT
                    address = address + mbi.RegionSize
                    continue
                
                memory_type = "Unknown"
                if mbi.Type == 0x20000:  # MEM_PRIVATE
                    memory_type = "Private"
                elif mbi.Type == 0x40000:  # MEM_MAPPED
                    memory_type = "Mapped"
                elif mbi.Type == 0x1000000:  # MEM_IMAGE
                    memory_type = "Image"
                
                # Create memory region object
                region = MemoryRegion(
                    base_address=int(mbi.BaseAddress),
                    size=mbi.RegionSize,
                    protection=mbi.Protect,
                    type_str=memory_type
                )
                
                memory_regions.append(region)
                
                # Move to next region
                address = int(mbi.BaseAddress) + mbi.RegionSize
            
            return memory_regions
        
        except Exception as e:
            logger.error(f"Error getting memory regions: {e}")
            return []

class LinuxProcessConnector(RealProcessConnector):
    """Linux-specific implementation using ptrace and /proc"""
    def __init__(self):
        super().__init__()
        if self.system != "Linux":
            raise RuntimeError("LinuxProcessConnector can only be used on Linux")
        
        # Import Linux-specific modules
        try:
            import psutil
            self.psutil = psutil
            self.has_modules = True
        except ImportError:
            logger.warning("Linux modules not available. Limited functionality.")
            self.has_modules = False
    
    def list_processes(self) -> List[ProcessInfo]:
        """List running processes on Linux"""
        if not self.has_modules:
            return []
        
        processes = []
        for proc in self.psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_info = ProcessInfo(
                    pid=proc.info['pid'],
                    name=proc.info['name'],
                    path=proc.info['exe']
                )
                processes.append(process_info)
            except (self.psutil.NoSuchProcess, self.psutil.AccessDenied, KeyError):
                pass
        
        return processes
    
    def attach_to_process(self, pid: int) -> bool:
        """Attach to a running process on Linux using ptrace"""
        try:
            # Check if process exists
            if not os.path.exists(f"/proc/{pid}"):
                logger.error(f"Process {pid} does not exist")
                return False
            
            # Use ptrace to attach
            libc = ctypes.CDLL("libc.so.6")
            PTRACE_ATTACH = 16
            
            result = libc.ptrace(PTRACE_ATTACH, pid, 0, 0)
            if result == -1:
                logger.error(f"Failed to attach to process {pid}")
                return False
            
            # Wait for the process to stop
            os.waitpid(pid, 0)
            
            self.process_handle = pid  # On Linux, we just use the PID
            self.attached_pid = pid
            logger.info(f"Successfully attached to process {pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error attaching to process: {e}")
            return False
    
    def detach_from_process(self) -> bool:
        """Detach from the currently attached process on Linux"""
        if not self._check_attached():
            return False
        
        try:
            # Use ptrace to detach
            libc = ctypes.CDLL("libc.so.6")
            PTRACE_DETACH = 17
            
            result = libc.ptrace(PTRACE_DETACH, self.attached_pid, 0, 0)
            if result == -1:
                logger.error(f"Failed to detach from process {self.attached_pid}")
                return False
            
            self.process_handle = None
            self.attached_pid = None
            logger.info("Successfully detached from process")
            return True
            
        except Exception as e:
            logger.error(f"Error detaching from process: {e}")
            return False
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from the attached process on Linux"""
        if not self._check_attached():
            return None
        
        try:
            # Read from /proc/[pid]/mem
            with open(f"/proc/{self.attached_pid}/mem", "rb") as mem_file:
                mem_file.seek(address)
                data = mem_file.read(size)
                return data
                
        except Exception as e:
            logger.error(f"Error reading memory: {e}")
            return None
    
    def write_memory(self, address: int, data: bytes) -> bool:
        """Write memory to the attached process on Linux"""
        if not self._check_attached():
            return False
        
        try:
            # Write to /proc/[pid]/mem
            with open(f"/proc/{self.attached_pid}/mem", "wb") as mem_file:
                mem_file.seek(address)
                mem_file.write(data)
                return True
                
        except Exception as e:
            logger.error(f"Error writing memory: {e}")
            return False
    
    def get_memory_regions(self) -> List[MemoryRegion]:
        """Get memory regions of the attached process on Linux"""
        if not self._check_attached():
            return []
        
        memory_regions = []
        
        try:
            # Parse /proc/[pid]/maps
            with open(f"/proc/{self.attached_pid}/maps", "r") as maps_file:
                for line in maps_file:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    
                    # Parse address range
                    addr_range = parts[0].split("-")
                    start_addr = int(addr_range[0], 16)
                    end_addr = int(addr_range[1], 16)
                    size = end_addr - start_addr
                    
                    # Parse permissions
                    perms = parts[1]
                    protection = 0
                    if 'r' in perms:
                        protection |= MemoryProtection.PROT_READ
                    if 'w' in perms:
                        protection |= MemoryProtection.PROT_WRITE
                    if 'x' in perms:
                        protection |= MemoryProtection.PROT_EXEC
                    
                    # Determine memory type and mapped file
                    mapped_file = parts[5] if len(parts) >= 6 else None
                    memory_type = "Mapped" if mapped_file else "Private"
                    
                    # Create memory region object
                    region = MemoryRegion(
                        base_address=start_addr,
                        size=size,
                        protection=protection,
                        type_str=memory_type,
                        mapped_file=mapped_file
                    )
                    
                    memory_regions.append(region)
            
            return memory_regions
                
        except Exception as e:
            logger.error(f"Error getting memory regions: {e}")
            return []

class MacOSProcessConnector(RealProcessConnector):
    """macOS-specific implementation using mach APIs"""
    def __init__(self):
        super().__init__()
        if self.system != "Darwin":
            raise RuntimeError("MacOSProcessConnector can only be used on macOS")
        
        # Import macOS-specific modules
        try:
            import psutil
            self.psutil = psutil
            self.has_modules = True
        except ImportError:
            logger.warning("macOS modules not available. Limited functionality.")
            self.has_modules = False
    
    def list_processes(self) -> List[ProcessInfo]:
        """List running processes on macOS"""
        if not self.has_modules:
            return []
        
        processes = []
        for proc in self.psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_info = ProcessInfo(
                    pid=proc.info['pid'],
                    name=proc.info['name'],
                    path=proc.info['exe']
                )
                processes.append(process_info)
            except (self.psutil.NoSuchProcess, self.psutil.AccessDenied, KeyError):
                pass
        
        return processes
    
    def attach_to_process(self, pid: int) -> bool:
        """Attach to a running process on macOS"""
        logger.warning("Process attachment on macOS requires higher privileges")
        logger.warning("This functionality may be limited due to System Integrity Protection")
        
        try:
            # Check if process exists
            if not self.has_modules:
                return False
            
            try:
                proc = self.psutil.Process(pid)
                proc_info = proc.as_dict(attrs=['pid', 'name'])
                if not proc_info:
                    logger.error(f"Process {pid} does not exist")
                    return False
            except self.psutil.NoSuchProcess:
                logger.error(f"Process {pid} does not exist")
                return False
            
            # Store process information
            self.process_handle = pid  # On macOS, we just use the PID
            self.attached_pid = pid
            logger.info(f"Successfully attached to process {pid}")
            logger.warning("Note: Memory access may be limited due to macOS security")
            return True
            
        except Exception as e:
            logger.error(f"Error attaching to process: {e}")
            return False
    
    def detach_from_process(self) -> bool:
        """Detach from the currently attached process on macOS"""
        if not self._check_attached():
            return False
        
        # Nothing special to do on macOS
        self.process_handle = None
        self.attached_pid = None
        logger.info("Successfully detached from process")
        return True
    
    def read_memory(self, address: int, size: int) -> Optional[bytes]:
        """Read memory from the attached process on macOS"""
        if not self._check_attached():
            return None
        
        logger.warning("Memory reading on macOS may be restricted")
        logger.error("Not implemented due to macOS security restrictions")
        return None
    
    def write_memory(self, address: int, data: bytes) -> bool:
        """Write memory to the attached process on macOS"""
        if not self._check_attached():
            return False
        
        logger.warning("Memory writing on macOS may be restricted")
        logger.error("Not implemented due to macOS security restrictions")
        return False
    
    def get_memory_regions(self) -> List[MemoryRegion]:
        """Get memory regions of the attached process on macOS"""
        if not self._check_attached():
            return []
        
        logger.warning("Memory region enumeration on macOS may be restricted")
        logger.error("Not implemented due to macOS security restrictions")
        return []

def create_process_connector() -> RealProcessConnector:
    """Create an appropriate process connector for the current platform"""
    system = platform.system()
    
    if system == "Windows":
        return WindowsProcessConnector()
    elif system == "Linux":
        return LinuxProcessConnector()
    elif system == "Darwin":  # macOS
        return MacOSProcessConnector()
    else:
        raise RuntimeError(f"Unsupported platform: {system}")