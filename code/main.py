from typing import List
import sys

import core.mess_with_pythonpath

from core.registers import Registers
from errors.core_errors import AddressError, ExitSignal, NullPtr, SegmentionFault, BadInstruction
from core.null import Null
from core.memory import Memory
from core.modes import AbsoluteMode, RelativeMode
from core.comp_types import *
import core.instructions as ins


class CPQUProcessor:
    """
    A bad processor.

    features that are not implemented are makred with a *

    On initialization, it takes a program (list of oprators) and writes it to its own memory, which the program can then use.

    The processor has a instruction pointer, which points to the current instruction being run.
    After a instruction is run, it increments the instruction pointer by (at least) 1, generaly by how many arguments it takes.
    however, some instructions can make the pointer jump to a new location.

    !important! mem address 1 is the first address!

    Each instruction has a mode before it (ex: <mode> <instruction>), which controlls how arguments are read from registers.
    A mode of abs means that it is the absolute index in memory, and a mode of rel means the relative position to the instruction pointer

    The processor also has 52 data registers, denoted by r<register code> where register code is any two letters (a-z), and a few special ones, including:
    out: the standard output. what is written to it will be outputted
    ins: the instruction pointer
    tru: a value of true
    fal: a value of false
    nul: null value, also behaves like /dev/null

    each register and all memory not used by the program is initialized to Null.

    It has a infinite memory size (at least not limited by the language),
    *although it must be allocated by the program to use it.

    TODO:
    $ come up with things to do? nah
    """
    def __init__(self, program: List[str] | str) -> None:
        if type(program) == str:
            program_opcodes = self.parse_program(program)
        else:
            program_opcodes = program
        self.inst_ptr = 0
        self.mem = Memory(program_opcodes)
        self.regs = Registers(self)

        self.exit_code = None
        self.exit_desc = None

    def run_till_done(self):
        while True:
            try:
                self.do_next_step()
            except BaseException as e:
                if isinstance(e, ExitSignal):
                    print(self.exit_desc)
                    print(f"Program exited with exit code {self.exit_code}")
                    break
                else:
                    print("error whilst running program!")
                    raise e
                

    def do_next_step(self):
        """
        Advance the computer to the next step, doing all processing for that step and updating all variables.
        """

        #~ get the next mode
        active_mode_string = self.mem.rat(self.inst_ptr)
        active_mode = self.parse_mode(active_mode_string)

        if active_mode is False:
            if self.parse_opcode(active_mode_string) is not False:
                active_mode = RelativeMode
            else:
                if active_mode_string == Null:
                    raise NullPtr(f"Encounterd Null value at {self.inst_ptr}, was expecting a instruction!")
                else:
                    raise BadInstruction(f"Encountered non-mode value {active_mode_string} at {self.inst_ptr}!!")
        else:
            self.inst_ptr += 1

        if active_mode is True:
            code = self.mem.rat(self.inst_ptr)
            try:
                code = int(code)
            except BaseException as e:
                self.exit_desc = f"could not parse exit code! it must be a number, not {code}"
                self.exit_code = 200
                raise ExitSignal()
                # raise e
            if code == 0:
                self.exit_desc = f"reached opcode `hlt` at addr {self.inst_ptr-1}, exiting gracefully with code {code}"
            else:
                self.exit_desc = f"reached opcode `hlt` at addr {self.inst_ptr-1}, exited with error code {code}"
            self.exit_code = code
            raise ExitSignal()
        
        if active_mode == ins.Syscall:
            #$ perform syscall
            self.regs.clear_syscall_res()
            id = self.regs.syscall_regs["syscl.id"]
            a1 = self.regs.syscall_regs["syscl.a1"]
            a2 = self.regs.syscall_regs["syscl.a2"]
            a3 = self.regs.syscall_regs["syscl.a3"]
            match id:
                case "malloc":
                    match a1:
                        case "extby":
                            #extends the memory by a2
                            amnt = int(a2)
                            self.mem.enlarge(amnt)
                            self.regs.add_syscall_res([True])
                        case "extto":
                            #extends the memory to addres in a2
                            amnt = int(a2)
                            self.mem.enlarge_to(amnt)
                            self.regs.add_syscall_res([True])
                    self.regs.clear_syscall_regs()
                case _:
                    self.regs.clear_syscall_regs()
                    self.regs.add_syscall_res([False])
            return

        #~ get the next opcode
        active_inst_string = self.mem.rat(self.inst_ptr)
        active_inst = self.parse_opcode(active_inst_string)
        if active_inst is False:
            raise BadInstruction(f"Encountered non-instruction {active_inst_string} at {self.inst_ptr}!!")

        #~ read the instruction's args
        args = []
        # print(self.inst_ptr)
        for i in range(active_inst.nargs):
            # print(self.mem.mem)
            # print(self.inst_ptr, self.mem.rat(self.inst_ptr))
            args.append(self.mem.rat(self.inst_ptr+i+1))
            # print(self.inst_ptr)

        # print(active_inst.__name__, args)
        # print(self.inst_ptr)

        #~ do a thing with that
        match active_inst:
            case ins.StoreTo:
                value_as_read = args[0]
                type = args[1]
                location_as_read = args[2]

                self.write_addr(location_as_read, value_as_read, active_mode, type)

                self.inst_ptr += active_inst.nargs+1

            case ins.StoreInequality:
                type_str = args[0]
                arg1_addr_as_read = args[1]
                arg2_addr_as_read = args[3]
                operator_as_read = args[2]
                dest_addr_as_read = args[4]

                arg1_val = self.cast_type(self.read_addr(arg1_addr_as_read, active_mode), type_str)
                arg2_val = self.cast_type(self.read_addr(arg2_addr_as_read, active_mode), type_str)
                operator = InequalityType(operator_as_read)

                result: bool

                match operator.value:
                    case "ltn":
                        result = arg1_val < arg2_val

                    case "gtn":
                        result = arg1_val > arg2_val

                    case "leq":
                        result = arg1_val <= arg2_val

                    case "geq":
                        result = arg1_val >= arg2_val

                    case "neq":
                        result = arg1_val != arg2_val

                    case "eqt":
                        result = arg1_val == arg2_val

                self.write_addr(dest_addr_as_read, result, active_mode, "bool")
                
                self.inst_ptr += active_inst.nargs+1

            case ins.CastTo:
                addr1 = args[0]
                cst_type = args[1]
                
                val = self.read_addr(addr1, active_mode)
                #~cast and write to the same addr
                self.write_addr(addr1, val, active_mode, cst_type)
                
                self.inst_ptr += active_inst.nargs+1

            case ins.AddTo:
                type_str = args[0]
                arg1_addr_as_read = args[1]
                arg2_addr_as_read = args[2]
                dest_addr_as_read = args[3]

                arg1_val = self.cast_type(self.read_addr(arg1_addr_as_read, active_mode), type_str)
                arg2_val = self.cast_type(self.read_addr(arg2_addr_as_read, active_mode), type_str)

                result = arg1_val + arg2_val

                self.write_addr(dest_addr_as_read, result, active_mode)

                self.inst_ptr += active_inst.nargs+1

            case ins.SubtractTo:
                type_str = args[0]
                arg1_addr_as_read = args[1]
                arg2_addr_as_read = args[2]
                dest_addr_as_read = args[3]

                arg1_val = self.cast_type(self.read_addr(arg1_addr_as_read, active_mode), type_str)
                arg2_val = self.cast_type(self.read_addr(arg2_addr_as_read, active_mode), type_str)

                result = arg1_val - arg2_val

                self.write_addr(dest_addr_as_read, result, active_mode)

                self.inst_ptr += active_inst.nargs+1

            case ins.DevideoTo:
                type_str = args[0]
                arg1_addr_as_read = args[1]
                arg2_addr_as_read = args[2]
                dest_addr_as_read = args[3]

                arg1_val = self.cast_type(self.read_addr(arg1_addr_as_read, active_mode), type_str)
                arg2_val = self.cast_type(self.read_addr(arg2_addr_as_read, active_mode), type_str)

                result = arg1_val / arg2_val

                self.write_addr(dest_addr_as_read, result, active_mode)

                self.inst_ptr += active_inst.nargs+1

            case ins.MultiplyTo:
                type_str1 = args[0]
                arg1_addr_as_read = args[1]
                type_str2 = args[2]
                arg2_addr_as_read = args[3]
                dest_addr_as_read = args[4]

                arg1_val = self.cast_type(self.read_addr(arg1_addr_as_read, active_mode), type_str1)
                arg2_val = self.cast_type(self.read_addr(arg2_addr_as_read, active_mode), type_str2)

                result = arg1_val * arg2_val

                self.write_addr(dest_addr_as_read, result, active_mode)

                self.inst_ptr += active_inst.nargs+1

            case ins.MoveTo:
                addr1 = args[0]
                addr2 = args[1]
                
                val = self.read_addr(addr1, active_mode)
                #~overwrite old val, as this is a move instruction, as long is it isnt "std" (stdin/stdout) to avoid writing null to stdout when moving from stdin
                if addr1 != "std":
                    self.write_addr(addr1, Null, active_mode)
                #~write val to new address
                self.write_addr(addr2, val, active_mode)
                
                self.inst_ptr += active_inst.nargs+1

            case ins.MoveIfEqual:
                arg1 = args[0]
                arg2 = args[1]
                addr1 = args[2]
                addr2 = args[3]

                if self.read_addr(arg1, active_mode) == self.read_addr(arg2, active_mode):
                    val = self.read_addr(addr1, active_mode)
                #~overwrite old val, as this is a move instruction, as long is it isnt "std" (stdin/stdout) to avoid writing null to stdout when moving from stdin
                if addr1 != "std":
                    self.write_addr(addr1, Null, active_mode)
                #~write val to new address
                self.write_addr(addr2, val, active_mode)

                self.inst_ptr += active_inst.nargs+1

            case ins.CopyTo:
                addr1 = args[0]
                addr2 = args[1]

                val = self.read_addr(addr1, active_mode)
                #~dont overwrite as this is copy not move
                #~write val to new address
                self.write_addr(addr2, val, active_mode)

                self.inst_ptr += active_inst.nargs+1

            case ins.CopyIfEqual:
                arg1 = args[0]
                arg2 = args[1]
                addr1 = args[2]
                addr2 = args[3]

                if self.read_addr(arg1, active_mode) == self.read_addr(arg2, active_mode):
                    val = self.read_addr(addr1, active_mode)
                    #~dont overwrite as this is copy not move
                    #~write val to new address
                    self.write_addr(addr2, val, active_mode)

                self.inst_ptr += active_inst.nargs+1

            case ins.JumpIfTrue:
                #~ find the location
                arg1_as_read = args[0]
                location_as_read = args[1]
                location = self.get_absolute_location(location_as_read, active_mode)

                #~ check if true
                read_value = self.read_addr(arg1_as_read, active_mode)
                is_true = self.cast_type(read_value, "bool")
                
                #~ jump to the location if true
                if is_true:
                    self.inst_ptr = location
                    # print(f"jumped to {self.inst_ptr}, value {self.mem.rat(self.inst_ptr)}")
                else:
                    self.inst_ptr += active_inst.nargs+1

            case ins.JumpTo:
                #~ find the location
                location_as_read = args[0]
                location = self.get_absolute_location(location_as_read, active_mode)

                #~ jump to the location
                self.inst_ptr = location
                
                # print(f"jumped to {self.inst_ptr}, value {self.mem.rat(self.inst_ptr)}")

            case _ as bad_inst:
                print(f"unknown instruction {bad_inst.__name__} with args {args}")
        
        # print(self.inst_ptr)

    def write_addr(self, addr: str, value, mode: RelativeMode | AbsoluteMode, cast_type=None,):
            if Registers.is_register(addr):
                if cast_type is not None:
                    self.regs.write(addr, self.cast_type(value, cast_type))
                else:
                    self.regs.write(addr, value)

            else:
                location = self.get_absolute_location(addr, mode)
                if cast_type is not None:
                    value = self.cast_type(value, cast_type)
                self.mem.wat(value, location)

    def read_addr(self, addr: str, mode: RelativeMode | AbsoluteMode):
        if Registers.is_register(addr):
            val = self.regs.read(addr)
            if val is AddressError:
                print("registry read error!!\nregistry dump:")
                print(self.regs.regs)
                raise AddressError(f"Cannot read from regestry {addr}!!")
            return val

        else:
            location = self.get_absolute_location(addr, mode)

            return self.mem.rat(location)

    def get_absolute_location(self, addr, mode):
        location: int

        if mode == RelativeMode:
            location = self.inst_ptr + int(addr)

        elif mode == AbsoluteMode:
            location = int(addr)

        return location

    def cast_type(self, value, type):
        match type:
            case "str":
                return str(value)
            case "int":
                return int(value)
            case "float":
                return float(value)
            case "bool":
                if value in ["True", "1", 1, True]:
                    return True
                elif value in ["False", "0", 0, False]:
                    return False
                else:
                    raise ValueError(f"cannot cast {value} to bool!")
            case _:
                raise ValueError(f"unknown type {type}")

    def parse_mode(self, mode_str):
        """
        parse a mode string to a mode class
        """
        match mode_str:
            case ins.ExitProgram.name:
                #exit program must be dealt with here, since it has no mode
                return True
            
            case ins.Syscall.name:
                return ins.Syscall

            case RelativeMode.name:
                return RelativeMode

            case AbsoluteMode.name:
                return AbsoluteMode

            case _:
                return False

    def parse_opcode(self, inst_str):
        """
        Parse a opcode to a instruction class
        """
        match inst_str:
            case ins.StoreTo.name:
                return ins.StoreTo

            case ins.StoreInequality.name:
                return ins.StoreInequality
            
            case ins.CastTo.name:
                return ins.CastTo

            case ins.AddTo.name:
                return ins.AddTo

            case ins.SubtractTo.name:
                return ins.SubtractTo

            case ins.MultiplyTo.name:
                return ins.MultiplyTo

            case ins.DevideoTo.name:
                return ins.DevideoTo

            case ins.MoveTo.name:
                return ins.MoveTo

            case ins.MoveIfEqual.name:
                return ins.MoveIfEqual

            case ins.CopyTo.name:
                return ins.CopyTo

            case ins.CopyIfEqual.name:
                return ins.CopyIfEqual

            case ins.JumpIfTrue.name:
                return ins.JumpIfTrue

            case ins.JumpTo.name:
                return ins.JumpTo

            case _:
                return False

    def parse_program(self, program: str) -> List[str]:
        """
        Basic parsing of the program into operations
        """
        codes = []

        next_code = ""
        in_ignore_block = False
        in_enclosing_block = False

        index = 0
        while True:
            next_char = program[index]
            # print(next_char)
            # print(in_enclosing_block)
            if next_char == "\"":
                # print("entering/exiting enclosing block")
                in_enclosing_block = not in_enclosing_block
            elif ((next_char == "#") and (not in_enclosing_block)):
                # print("entering comment block")
                in_ignore_block = True
            elif ((next_char == "\n") and in_ignore_block):
                # print("exiting comment block")
                in_ignore_block = False
            else:
                if (((next_char not in [" ", "\n"]) or (in_enclosing_block)) and (not in_ignore_block)):
                    next_code += next_char
                else:
                    if next_code != "":
                        codes.append(next_code)
                        next_code = ""
            if index < len(program)-1:
                index += 1
            else:
                codes.append(next_code)
                break

        return [code for code in codes if code not in [""]]



with open(sys.argv[1], "r") as f:
    program = f.read()

computer = CPQUProcessor(program)

print(computer.mem.size())
print(computer.mem.mem)

computer.run_till_done()