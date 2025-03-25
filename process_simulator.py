import uuid
import logging
import random
import copy
from typing import Dict, List, Any, Optional, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Instruction types for simulation
class InstructionType:
    MOV = "mov"
    ADD = "add"
    SUB = "sub"
    JMP = "jmp"
    CMP = "cmp"
    JE = "je"
    CALL = "call"
    RET = "ret"
    NOP = "nop"

class Instruction:
    """Represents a simulated instruction"""
    def __init__(self, address: str, opcode: str, operands: List[str], bytes_repr: str):
        self.address = address
        self.opcode = opcode  # e.g., MOV, ADD, etc.
        self.operands = operands  # e.g., ['eax', '[ebx+4]']
        self.bytes = bytes_repr  # Hexadecimal representation of instruction
        
    def __str__(self):
        operands_str = ", ".join(self.operands)
        return f"{self.address}: {self.opcode} {operands_str}"

class Breakpoint:
    """Represents a breakpoint in memory"""
    def __init__(self, address: str, bp_type: str, condition: Optional[str] = None, enabled: bool = True):
        self.address = address
        self.type = bp_type  # "execution", "read", "write", or "access"
        self.condition = condition  # Optional condition expression
        self.enabled = enabled
        self.hit_count = 0
    
    def __str__(self):
        return f"BP at {self.address} ({self.type}) - {'Enabled' if self.enabled else 'Disabled'}"

class Symbol:
    """Represents a symbol or label in the code"""
    def __init__(self, address: str, name: str, symbol_type: str = "function"):
        self.address = address
        self.name = name
        self.type = symbol_type  # "function", "variable", etc.
    
    def __str__(self):
        return f"{self.name} ({self.type}) at {self.address}"

class SimulatedProcess:
    """Class representing a simulated process with memory, registers, and code"""
    
    def __init__(self, name: str, pid: str, memory: Optional[Dict[str, Any]] = None):
        self.name = name
        self.pid = pid
        self.memory = memory or {}
        
        # CPU registers (x86_64 style)
        self.registers = {
            "rax": 0, "rbx": 0, "rcx": 0, "rdx": 0,
            "rsi": 0, "rdi": 0, "rbp": 0, "rsp": 0,
            "r8": 0, "r9": 0, "r10": 0, "r11": 0,
            "r12": 0, "r13": 0, "r14": 0, "r15": 0,
            "rip": 0, "rflags": 0,
            "cf": 0, "zf": 0, "sf": 0, "of": 0  # Individual flags
        }
        
        # Stack memory
        self.stack = {}
        self.stack_base = 0xFFFF0000  # Example base address for stack
        self.stack_size = 0x10000  # 64KB stack
        
        # Code & instructions
        self.instructions = {}  # address -> Instruction object
        self.code_base = 0x400000  # Base address for code
        
        # Breakpoints
        self.breakpoints = {}  # address -> Breakpoint object
        
        # Symbols/labels
        self.symbols = {}  # address -> Symbol object
        self.symbols_by_name = {}  # name -> Symbol object
        
        # Execution state
        self.running = False
        self.step_mode = False
        
        # Memory access history for undo/redo
        self.memory_history = []
        self.history_position = -1
        
    def __str__(self):
        return f"{self.name} (PID: {self.pid})"
    
    def save_memory_state(self):
        """Save current memory state for undo/redo"""
        # Remove any states after current position if we're in the middle
        if self.history_position < len(self.memory_history) - 1:
            self.memory_history = self.memory_history[:self.history_position + 1]
        
        # Create a deep copy of the current memory
        mem_copy = copy.deepcopy(self.memory)
        self.memory_history.append(mem_copy)
        self.history_position = len(self.memory_history) - 1
        
        # Keep history size manageable
        if len(self.memory_history) > 50:  # Limit to 50 states
            self.memory_history.pop(0)
            self.history_position -= 1
    
    def undo_memory_change(self) -> bool:
        """Undo the last memory change"""
        if self.history_position > 0:
            self.history_position -= 1
            self.memory = copy.deepcopy(self.memory_history[self.history_position])
            return True
        return False
    
    def redo_memory_change(self) -> bool:
        """Redo a previously undone memory change"""
        if self.history_position < len(self.memory_history) - 1:
            self.history_position += 1
            self.memory = copy.deepcopy(self.memory_history[self.history_position])
            return True
        return False

class ProcessSimulator:
    """Class for simulating processes that can be attached to for memory editing and debugging"""
    
    def __init__(self):
        self.processes: Dict[str, SimulatedProcess] = {}
        self.current_process: Optional[str] = None
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
        
        # Create the process
        process = SimulatedProcess(name, pid, initial_memory)
        
        # Generate some sample code and symbols for the process
        self._generate_sample_code(process)
        
        # Set up initial memory state for undo/redo
        process.save_memory_state()
        
        self.processes[pid] = process
        logger.debug(f"Created process: {name} with PID: {pid}")
        return pid
    
    def _generate_sample_code(self, process: SimulatedProcess) -> None:
        """Generate sample instructions and symbols for the process"""
        # Sample functions and their code
        functions = [
            ("main", 0x400500),
            ("calculate", 0x400600),
            ("print_result", 0x400700),
            ("handle_error", 0x400800)
        ]
        
        # Create symbols for functions
        for name, addr in functions:
            address = hex(addr)
            symbol = Symbol(address, name, "function")
            process.symbols[address] = symbol
            process.symbols_by_name[name] = symbol
        
        # Create some global variables as symbols
        variables = [
            ("counter", 0x601000, 0),
            ("result", 0x601008, 0),
            ("message", 0x601010, "Hello, Debugger!")
        ]
        
        for name, addr, value in variables:
            address = hex(addr)
            symbol = Symbol(address, name, "variable")
            process.symbols[address] = symbol
            process.symbols_by_name[name] = symbol
            process.memory[address] = value
        
        # Generate instructions for main
        main_addr = 0x400500
        instructions = [
            (main_addr, InstructionType.MOV, ["rax", "0"], "48 c7 c0 00 00 00 00"),
            (main_addr + 7, InstructionType.MOV, ["rbx", "10"], "48 c7 c3 0a 00 00 00"),
            (main_addr + 14, InstructionType.CALL, [hex(0x400600)], "e8 e7 00 00 00"),
            (main_addr + 19, InstructionType.CMP, ["rax", "0"], "48 83 f8 00"),
            (main_addr + 23, InstructionType.JE, [hex(0x400800)], "0f 84 d7 02 00 00"),
            (main_addr + 29, InstructionType.CALL, [hex(0x400700)], "e8 d2 01 00 00"),
            (main_addr + 34, InstructionType.RET, [], "c3")
        ]
        
        # Add instructions to process
        for addr, opcode, operands, bytes_repr in instructions:
            address = hex(addr)
            instr = Instruction(address, opcode, operands, bytes_repr)
            process.instructions[address] = instr
        
        # Set initial RIP to main
        process.registers["rip"] = main_addr
    
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
        
        # Save current state for undo/redo
        process.save_memory_state()
        
        # Check if any breakpoints might be triggered (memory write breakpoints)
        self._check_memory_breakpoints(process, address, "write")
        
        # Write the value
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
    
    def get_registers(self, pid: str) -> Dict[str, int]:
        """Get the CPU registers for a process"""
        process = self.get_process(pid)
        if not process:
            logger.warning(f"Process {pid} not found")
            return {}
        
        return process.registers
    
    def set_register(self, pid: str, register: str, value: int) -> bool:
        """Set a CPU register to a specific value"""
        process = self.get_process(pid)
        if not process or register not in process.registers:
            return False
        
        process.registers[register] = value
        logger.debug(f"Set register {register} to {value} for process {pid}")
        return True
    
    def get_instructions(self, pid: str, start_address: Optional[str] = None, count: int = 10) -> List[Instruction]:
        """Get a list of instructions starting from the given address"""
        process = self.get_process(pid)
        if not process:
            return []
        
        if not start_address:
            # Use current instruction pointer if no address specified
            start_address = hex(process.registers["rip"])
        
        # Get all instruction addresses and sort them
        addresses = sorted([int(addr, 16) for addr in process.instructions.keys()])
        
        # Find the start address in the sorted list
        start_addr_int = int(start_address, 16)
        start_idx = 0
        for i, addr in enumerate(addresses):
            if addr >= start_addr_int:
                start_idx = i
                break
        
        # Get up to 'count' instructions from that point
        result = []
        for i in range(start_idx, min(start_idx + count, len(addresses))):
            addr = hex(addresses[i])
            result.append(process.instructions[addr])
        
        return result
    
    def set_breakpoint(self, pid: str, address: str, bp_type: str = "execution", condition: Optional[str] = None) -> bool:
        """Set a breakpoint at the specified address"""
        process = self.get_process(pid)
        if not process:
            return False
        
        bp = Breakpoint(address, bp_type, condition)
        process.breakpoints[address] = bp
        logger.debug(f"Set {bp_type} breakpoint at {address} for process {pid}")
        return True
    
    def remove_breakpoint(self, pid: str, address: str) -> bool:
        """Remove a breakpoint at the specified address"""
        process = self.get_process(pid)
        if not process or address not in process.breakpoints:
            return False
        
        del process.breakpoints[address]
        logger.debug(f"Removed breakpoint at {address} for process {pid}")
        return True
    
    def get_breakpoints(self, pid: str) -> List[Breakpoint]:
        """Get all breakpoints for a process"""
        process = self.get_process(pid)
        if not process:
            return []
        
        return list(process.breakpoints.values())
    
    def toggle_breakpoint(self, pid: str, address: str) -> Tuple[bool, bool]:
        """Toggle a breakpoint on/off, returns (success, new_state)"""
        process = self.get_process(pid)
        if not process or address not in process.breakpoints:
            return False, False
        
        bp = process.breakpoints[address]
        bp.enabled = not bp.enabled
        logger.debug(f"Toggled breakpoint at {address} to {bp.enabled} for process {pid}")
        return True, bp.enabled
    
    def get_symbols(self, pid: str) -> List[Symbol]:
        """Get all symbols for a process"""
        process = self.get_process(pid)
        if not process:
            return []
        
        return list(process.symbols.values())
    
    def lookup_symbol(self, pid: str, name: str) -> Optional[Symbol]:
        """Look up a symbol by name"""
        process = self.get_process(pid)
        if not process:
            return None
        
        return process.symbols_by_name.get(name)
    
    def get_address_symbol(self, pid: str, address: str) -> Optional[Symbol]:
        """Get symbol at a specific address"""
        process = self.get_process(pid)
        if not process:
            return None
        
        return process.symbols.get(address)
    
    def step_instruction(self, pid: str) -> bool:
        """Step a single instruction in the process"""
        process = self.get_process(pid)
        if not process:
            return False
        
        # Get current instruction pointer
        rip = process.registers["rip"]
        next_rip = self._execute_instruction(process, hex(rip))
        
        # Update instruction pointer
        process.registers["rip"] = next_rip
        logger.debug(f"Stepped instruction in process {pid}, RIP now {hex(next_rip)}")
        return True
    
    def run_until_breakpoint(self, pid: str, max_steps: int = 1000) -> bool:
        """Run the process until a breakpoint is hit or max_steps is reached"""
        process = self.get_process(pid)
        if not process:
            return False
        
        process.running = True
        steps = 0
        
        while process.running and steps < max_steps:
            rip = process.registers["rip"]
            rip_hex = hex(rip)
            
            # Check if we hit an execution breakpoint
            if rip_hex in process.breakpoints and process.breakpoints[rip_hex].enabled:
                bp = process.breakpoints[rip_hex]
                if bp.type == "execution":
                    bp.hit_count += 1
                    logger.debug(f"Hit execution breakpoint at {rip_hex}")
                    process.running = False
                    return True
            
            # Execute current instruction
            next_rip = self._execute_instruction(process, rip_hex)
            
            # Update instruction pointer
            process.registers["rip"] = next_rip
            steps += 1
        
        process.running = False
        return True
    
    def _execute_instruction(self, process: SimulatedProcess, address: str) -> int:
        """Execute the instruction at the given address and return next instruction address"""
        if address not in process.instructions:
            # If no instruction at this address, just advance by 1
            return int(address, 16) + 1
        
        instr = process.instructions[address]
        rip = int(address, 16)
        next_rip = rip
        
        # Very simple instruction simulation
        if instr.opcode == InstructionType.MOV:
            # Handle MOV instruction (dst, src)
            dst, src = instr.operands
            
            # Get the source value
            if src.isdigit() or (src.startswith('-') and src[1:].isdigit()):
                value = int(src)
            elif src.startswith('0x'):
                value = int(src, 16)
            else:
                # Assume it's a register
                value = process.registers.get(src, 0)
            
            # Set the destination
            if dst in process.registers:
                process.registers[dst] = value
            else:
                # Assume it's a memory address
                process.memory[dst] = value
            
            # Determine length of instruction (simplified)
            next_rip = rip + len(instr.bytes.split()) // 2
        
        elif instr.opcode == InstructionType.ADD:
            # Handle ADD instruction (dst, src)
            dst, src = instr.operands
            
            # Get the source value
            if src.isdigit() or (src.startswith('-') and src[1:].isdigit()):
                value = int(src)
            elif src.startswith('0x'):
                value = int(src, 16)
            else:
                # Assume it's a register
                value = process.registers.get(src, 0)
            
            # Add to destination
            if dst in process.registers:
                process.registers[dst] += value
            else:
                # Assume it's a memory address
                if dst in process.memory:
                    process.memory[dst] += value
            
            next_rip = rip + len(instr.bytes.split()) // 2
        
        elif instr.opcode == InstructionType.SUB:
            # Similar to ADD but subtract
            dst, src = instr.operands
            
            if src.isdigit() or (src.startswith('-') and src[1:].isdigit()):
                value = int(src)
            elif src.startswith('0x'):
                value = int(src, 16)
            else:
                value = process.registers.get(src, 0)
            
            if dst in process.registers:
                process.registers[dst] -= value
            else:
                if dst in process.memory:
                    process.memory[dst] -= value
            
            next_rip = rip + len(instr.bytes.split()) // 2
        
        elif instr.opcode == InstructionType.JMP:
            # Unconditional jump
            target = instr.operands[0]
            if target.startswith('0x'):
                next_rip = int(target, 16)
            else:
                # Try to resolve symbol
                symbol = process.symbols_by_name.get(target)
                if symbol:
                    next_rip = int(symbol.address, 16)
        
        elif instr.opcode == InstructionType.CMP:
            # Compare two values and set flags
            left, right = instr.operands
            
            # Get left value
            if left in process.registers:
                left_val = process.registers[left]
            else:
                left_val = int(left, 0) if left.startswith('0x') else int(left)
            
            # Get right value
            if right in process.registers:
                right_val = process.registers[right]
            else:
                right_val = int(right, 0) if right.startswith('0x') else int(right)
            
            # Set flags
            process.registers['zf'] = 1 if left_val == right_val else 0
            process.registers['sf'] = 1 if left_val < right_val else 0
            
            next_rip = rip + len(instr.bytes.split()) // 2
        
        elif instr.opcode == InstructionType.JE:
            # Jump if equal (ZF=1)
            if process.registers['zf'] == 1:
                target = instr.operands[0]
                if target.startswith('0x'):
                    next_rip = int(target, 16)
                else:
                    symbol = process.symbols_by_name.get(target)
                    if symbol:
                        next_rip = int(symbol.address, 16)
            else:
                next_rip = rip + len(instr.bytes.split()) // 2
        
        elif instr.opcode == InstructionType.CALL:
            # Push return address to stack and jump
            target = instr.operands[0]
            ret_addr = rip + len(instr.bytes.split()) // 2
            
            # Push return address to stack
            rsp = process.registers['rsp'] - 8  # Decrement stack pointer (x86_64 uses 8 bytes)
            process.registers['rsp'] = rsp
            process.memory[hex(rsp)] = ret_addr
            
            # Jump to target
            if target.startswith('0x'):
                next_rip = int(target, 16)
            else:
                symbol = process.symbols_by_name.get(target)
                if symbol:
                    next_rip = int(symbol.address, 16)
        
        elif instr.opcode == InstructionType.RET:
            # Pop return address from stack
            rsp = process.registers['rsp']
            if hex(rsp) in process.memory:
                next_rip = process.memory[hex(rsp)]
                process.registers['rsp'] = rsp + 8  # Increment stack pointer
        
        else:
            # Default: just move to next instruction
            next_rip = rip + len(instr.bytes.split()) // 2
        
        return next_rip
    
    def _check_memory_breakpoints(self, process: SimulatedProcess, address: str, access_type: str) -> None:
        """Check if any memory access breakpoints are triggered"""
        if address in process.breakpoints:
            bp = process.breakpoints[address]
            if bp.enabled and (bp.type == access_type or bp.type == "access"):
                bp.hit_count += 1
                logger.debug(f"Hit {access_type} breakpoint at {address}")
                process.running = False
    
    def undo_memory_edit(self, pid: str) -> bool:
        """Undo the last memory edit"""
        process = self.get_process(pid)
        if not process:
            return False
        
        return process.undo_memory_change()
    
    def redo_memory_edit(self, pid: str) -> bool:
        """Redo a previously undone memory edit"""
        process = self.get_process(pid)
        if not process:
            return False
        
        return process.redo_memory_change()
