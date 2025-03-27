"""
Android Process Connector for Memory Debugger.
Provides integration with the Android version of the application.
"""
import json
import os
import platform
import subprocess
from typing import Dict, List, Optional, Any, Tuple

# This module serves as a placeholder for Android-specific functionality 
# that would be implemented in the native Android application.
# It also serves as a design reference for the Android implementation.

class AndroidProcessConnector:
    """Android-specific implementation to interface with Android app"""
    def __init__(self):
        self.connected = False
        self.current_pid = None
        self.device_id = None
        self.using_shizuku = False  # Flag to indicate whether to use Shizuku API
    
    def is_android_connected(self) -> bool:
        """Check if an Android device is connected via ADB"""
        try:
            # Check if adb is installed
            subprocess.run("adb version", 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True,
                          shell=True)
            
            # Get list of connected devices
            result = subprocess.run("adb devices", 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   check=True, 
                                   text=True,
                                   shell=True)
            
            # Parse output to check for connected devices
            lines = result.stdout.strip().split('\n')
            if len(lines) <= 1:  # Only "List of devices attached" line
                return False
            
            for line in lines[1:]:
                if line.strip() and "device" in line:
                    # Extract device ID
                    self.device_id = line.split()[0]
                    return True
            
            return False
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """List running processes on the connected Android device"""
        if not self.is_android_connected():
            return []
        
        try:
            # Use ADB to get process list
            cmd = f"adb -s {self.device_id} shell ps -e"
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   check=True, 
                                   text=True,
                                   shell=True)
            
            processes = []
            lines = result.stdout.strip().split('\n')
            
            # Skip header line
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 8:  # Standard ps format
                    pid = parts[1]
                    name = parts[-1]  # Process name is typically the last column
                    
                    processes.append({
                        "pid": pid,
                        "name": name,
                        "type": "android",
                        "status": "running"
                    })
            
            return processes
        except subprocess.SubprocessError:
            return []
    
    def attach_to_process(self, pid: str) -> bool:
        """Attach to a process on the Android device"""
        if not self.is_android_connected():
            return False
        
        # Verify the process exists
        processes = self.list_processes()
        for process in processes:
            if process["pid"] == pid:
                self.current_pid = pid
                self.connected = True
                return True
        
        return False
    
    def detach_from_process(self) -> bool:
        """Detach from the current process"""
        self.current_pid = None
        self.connected = False
        return True
    
    def read_memory(self, address: str, size: int = 8) -> Optional[bytes]:
        """Read memory from the attached process (requires root)"""
        if not self.connected or not self.current_pid:
            return None
        
        try:
            # Note: This requires a rooted device and would be implemented in the Android app
            # This is a placeholder that would use native code in the actual Android app
            
            # Attempt to read memory using ADB and su (for rooted devices)
            dd_cmd = f"dd if=/proc/{self.current_pid}/mem bs=1 count={size} skip={int(address, 16)} 2>/dev/null | xxd -p"
            adb_cmd = f"adb -s {self.device_id} shell su -c '{dd_cmd}'"
            result = subprocess.run(adb_cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   check=True, 
                                   text=True,
                                   shell=True)
            
            # Convert hex string to bytes
            hex_str = result.stdout.strip().replace("\n", "")
            if hex_str:
                return bytes.fromhex(hex_str)
            
            return None
        except (subprocess.SubprocessError, ValueError):
            return None
    
    def write_memory(self, address: str, value: bytes) -> bool:
        """Write memory to the attached process (requires root)"""
        if not self.connected or not self.current_pid:
            return False
        
        try:
            # Note: This is a placeholder that would use native code in the Android app
            # Writing memory on Android requires root and would be better implemented in C/C++
            
            # This is extremely difficult to do with ADB shell alone
            # In the Android app, this would use a native library with memory access APIs
            return False
        except subprocess.SubprocessError:
            return False
    
    def get_memory_regions(self) -> List[Dict[str, Any]]:
        """Get memory regions of the attached process"""
        if not self.connected or not self.current_pid:
            return []
        
        try:
            # Read memory maps from /proc/{pid}/maps
            cat_cmd = f"cat /proc/{self.current_pid}/maps"
            adb_cmd = f"adb -s {self.device_id} shell su -c '{cat_cmd}'"
            result = subprocess.run(adb_cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   check=True, 
                                   text=True,
                                   shell=True)
            
            regions = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    addr_range = parts[0].split('-')
                    if len(addr_range) == 2:
                        base_addr = int(addr_range[0], 16)
                        end_addr = int(addr_range[1], 16)
                        size = end_addr - base_addr
                        
                        perms = parts[1]
                        offset = parts[2]
                        dev = parts[3]
                        inode = parts[4]
                        
                        path = " ".join(parts[5:]) if len(parts) > 5 else ""
                        
                        regions.append({
                            "base_address": hex(base_addr),
                            "end_address": hex(end_addr),
                            "size": size,
                            "permissions": perms,
                            "path": path,
                            "type": "mapped" if path else "anonymous"
                        })
            
            return regions
        except subprocess.SubprocessError:
            return []
    
    def is_device_rooted(self) -> bool:
        """Check if the Android device is rooted"""
        if not self.is_android_connected():
            return False
        
        try:
            # Try running a command that requires root
            adb_cmd = f"adb -s {self.device_id} shell su -c 'id'"
            result = subprocess.run(adb_cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   shell=True)
            
            # If command succeeds and contains "uid=0", the device is rooted
            return "uid=0" in result.stdout
        except subprocess.SubprocessError:
            return False
    
    def get_android_version(self) -> str:
        """Get the Android version of the connected device"""
        if not self.is_android_connected():
            return "Unknown"
        
        try:
            adb_cmd = f"adb -s {self.device_id} shell getprop ro.build.version.release"
            result = subprocess.run(adb_cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   check=True, 
                                   text=True,
                                   shell=True)
            
            return result.stdout.strip()
        except subprocess.SubprocessError:
            return "Unknown"
            
    def use_shizuku(self) -> bool:
        """Configure to use Shizuku instead of direct root"""
        self.using_shizuku = True
        return True
        
    def is_shizuku_available(self) -> bool:
        """Check if Shizuku is available on the device"""
        if not self.is_android_connected():
            return False
            
        # Use adb to check if Shizuku is installed
        result = subprocess.run(
            ["adb", "shell", "pm", "list", "packages", "moe.shizuku.privileged.api"],
            capture_output=True,
            text=True
        )
        
        return "moe.shizuku.privileged.api" in result.stdout
        
    def read_memory_shizuku(self, pid: str, address: str, size: int = 8) -> Optional[bytes]:
        """Read memory using Shizuku API rather than root"""
        if not self.using_shizuku or not self.is_shizuku_available():
            return None
            
        # In the actual implementation, this would call the Shizuku API
        # through the Android app's native code. This is just a placeholder.
        print(f"Reading memory via Shizuku: pid={pid}, address={address}, size={size}")
        return b'\x00' * size
        
    def write_memory_shizuku(self, pid: str, address: str, value: bytes) -> bool:
        """Write memory using Shizuku API rather than root"""
        if not self.using_shizuku or not self.is_shizuku_available():
            return False
            
        # In the actual implementation, this would call the Shizuku API
        # through the Android app's native code. This is just a placeholder.
        print(f"Writing memory via Shizuku: pid={pid}, address={address}, value={value.hex()}")
        return True

# Helper function to check if running on Android
def is_running_on_android() -> bool:
    """Check if the current platform is Android"""
    return "android" in platform.platform().lower()