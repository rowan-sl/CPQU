from typing import List
import sys
import logging
logger = logging.getLogger("CPUProc")

import core.mess_with_pythonpath

from core.lang.registers import Registers
from core.errors.comp_errors import (
    AddressError,
    ExitSignal,
    NullPtr,
    SegmentionFault,
    BadInstruction
)
from core.types.null import Null
from core.lang.memory import Memory
from core.lang.assembler import Assembler
from core.lang.builtins import Builtins
from core.types.modes import (
    AbsoluteMode,
    RelativeMode
)
from core.types.comp_types import (
    InequalityType,
    Address
)
import core.types.instructions as ins
#macros
from core.lang.macros.end_fail_macro import (
    EndMacro,
    FailMacro
)
from core.lang.macros.print_macro import PrintMacro


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

    &There is also the instruction `nop` which does nothing. very efficiently


    &HOWEVER:
    The addresses can be messed with when expanding macros, so please use address notation instead.

    Addresses are defined with `@name` and referenced with `$name`.

    The definition of a address means that a reference to that address will be replaced with the next thing after the adress definition, and the address definition will be replaced with nop

    Address names must match the regular expresion [a-zA-Z1234567890_] (only alphabet letters, numbers, or underscores).

    Adresses are globaly defined, no two addresses can have the same name.

    Adresses are expanded to numbers in preprocessing, so self modifying code must use number references.
    
    In addition, when refering to a address, you can provide the value as a register, using `*reg_name`


    The processor also has 52 data registers, denoted by r<register code> where register code is any two letters (a-z), and a few special ones, including:
    out: the standard output. what is written to it will be outputted
    ins: the instruction pointer
    tru: a value of true
    fal: a value of false
    nul: null value, also behaves like /dev/null

    each register and all memory not used by the program is initialized to Null.

    It has a infinite memory size (at least not limited by the language),
    although it must be allocated by the program to use it.


    It also has some basic macros, including:

    `end`: basicaly `hlt 0`
    `fail<--insert reason here-->`: basicaly `sto --insert reason here-- str out hlt 1`

    TODO:

    $ implement address notation

    $ more macros?
    """

    macro_list = [
        EndMacro,
        FailMacro,
        PrintMacro,
    ]

    def __init__(self) -> None:
        self.debug = False#! REMOVE THIS AND REPLACE w/ LOGGER
        self.inst_ptr = 0
        self.mem = Memory([], self.debug)
        self.regs = Registers(self, self.debug)
        self.builtins = Builtins()
        self.assembler = Assembler(self.macro_list)

        self.exit_code = None
        self.exit_desc = None

    def reset(self):
        """
        Resets the computer, clearing all memory and data
        """
        self.inst_ptr = 0
        self.regs.reset()
        self.mem.reset()
        self.builtins = Builtins()
        self.assembler = Assembler(self.macro_list)

        self.exit_code = None
        self.exit_desc = None

    def load_program(self, program: str|list, compiled: bool=False):
        if not compiled:
            parsed_program = self.assembler.assemble(program)
        else:
            parsed_program = program
        self.mem.load_memory(parsed_program)

    def run_till_done(self):
        while True:
            try:
                self.do_next_step()
            except BaseException as e:
                if isinstance(e, ExitSignal):
                    logger.info(f"Program exited with desc:\n{self.exit_desc}\nand exit code {self.exit_code}")
                    break
                else:
                    logger.critical("error whilst running program!")
                    logger.critical(e)
                    logger.critical("Exiting because of program error")
                    raise e

        return self.exit_code

    def do_next_step(self):
        """
        Advance the computer to the next step, doing all processing for that step and updating all variables.
        """
        logger.inst_trace(f"Doing next step for program. ins_ptr: {self.inst_ptr} mem @ ins_ptr: {self.mem.rat(self.inst_ptr)}")

        #~ get the next mode
        active_mode_string = self.mem.rat(self.inst_ptr)
        if active_mode_string == "nop":
            logger.inst_call(f"nop instruction at address {self.inst_ptr}")
            #! do nothing, this is where nop is defined
            self.inst_ptr += 1
            return
        active_mode = self.parse_mode(active_mode_string)

        if active_mode is False:
            if self.parse_opcode(active_mode_string) is not False:
                logger.inst_trace(f"Inferring absolute mode at address {self.inst_ptr}")
                active_mode = AbsoluteMode
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
            logger.inst_call(f"Syscall triggered at address {self.inst_ptr-1}")
            #$ perform syscall
            self.regs.clear_syscall_res()
            id = self.regs.syscall_regs["syscl.id"]
            a1 = self.regs.syscall_regs["syscl.a1"]
            a2 = self.regs.syscall_regs["syscl.a2"]
            a3 = self.regs.syscall_regs["syscl.a3"]
            logger.inst_call(f"Syscall args:\nid:{id}\na1:{a1}\na2:{a2}\na3:{a3}")
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
                case "rfile":
                    assert a1 != ""
                    assert self.regs.is_register(a2)
                    try:
                        with open(a1, "r") as f:
                            content = f.read()
                        self.regs.write(a2, content)
                        self.regs.add_syscall_res([True])
                    except FileNotFoundError as e:
                        logger.program_state(f"Error whilest reading file for program:\n{e}")
                        self.regs.add_syscall_res([False])
                    self.regs.clear_syscall_regs()
                case _:
                    self.regs.clear_syscall_regs()
                    self.regs.add_syscall_res([False])
            return

        #~ get the next opcode
        active_inst_string = self.mem.rat(self.inst_ptr)
        active_inst = self.parse_opcode(active_inst_string)
        logger.inst_trace(f"getting args for opcode {active_inst} ({active_inst_string}) at addr {self.inst_ptr}")
        if active_inst is False:
            raise BadInstruction(f"Encountered non-instruction {active_inst_string} at {self.inst_ptr}!!")

        #~ read the instruction's args
        args = []
        logger.mem_trace(f"Reading instructions for opcode")
        for i in range(active_inst.nargs):
            logger.mem_trace(f"reading value from address {self.inst_ptr+i+1} for opcode args")
            args.append(self.mem.rat(self.inst_ptr+i+1))

        logger.inst_call(f"running opcode {active_inst.__name__} with args {args}")

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
                
                logging.spam(f"Store inequality with {arg1_val} {operator.value} {arg2_val}")

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
                    logger.ins_trace(f"jumped to {self.inst_ptr}, value {self.mem.rat(self.inst_ptr)}")
                else:
                    self.inst_ptr += active_inst.nargs+1

            case ins.JumpTo:
                #~ find the location
                location_as_read = args[0]
                location = self.get_absolute_location(location_as_read, active_mode)

                #~ jump to the location
                self.inst_ptr = location

                logger.ins_trace(f"jumped to {self.inst_ptr}, value {self.mem.rat(self.inst_ptr)}")

            case ins.StoreStringIndex:
                in_str_addr = args[0]
                index_str = args[1]
                out_addr = args[2]

                in_str = self.read_addr(in_str_addr, active_mode)
                index = self.cast_type(index_str, "int")
                value_at_i = in_str[index]
                self.write_addr(out_addr, value_at_i, active_mode)
                
                self.inst_ptr += active_inst.nargs+1

            case ins.StoreStringLen:
                string = args[0]
                addr2 = args[1]

                val = self.read_addr(string, active_mode)

                #~write len of val to new address
                self.write_addr(addr2, len(val), active_mode)

                self.inst_ptr += active_inst.nargs+1

            case _ as bad_inst:
                print(f"unknown instruction {bad_inst.__name__} with args {args}")

        # print(self.inst_ptr)

    def write_addr(self, addr: str, value, mode: RelativeMode | AbsoluteMode, cast_type=None,):
        logger.comp_func(f"Calling write_addr with args {addr} {value} {mode} {cast_type}")
        if addr.startswith("*"):
            if Registers.is_register(addr[1:]):
                #writing to a address, but from the address stored in a register
                deref_addr = self.regs.read(addr[1:])

                location = self.get_absolute_location(deref_addr, mode)
                if cast_type is not None:
                    value = self.cast_type(value, cast_type)
                self.mem.wat(value, location)

        else:
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
        logger.comp_func(f"calling read_addr with args {addr} {mode}")
        if addr.startswith("*"):
            if Registers.is_register(addr[1:]):
                #reading from a address, but from the address stored in a register
                deref_addr = self.regs.read(addr[1:])

                location = self.get_absolute_location(deref_addr, mode)
                vat = self.mem.rat(location)
                logger.spam(f"Read value {vat}")
                return vat

        else:
            if Registers.is_register(addr):
                val = self.regs.read(addr)
                if val is AddressError:
                    logger.error(f"registry read error!!\nregistry dump:\n{self.regs.regs}")
                    raise AddressError(f"Cannot read from regestry {addr}!!")
                logger.spam(f"Read value {val}")
                return val

            else:
                location = self.get_absolute_location(addr, mode)

                val = self.mem.rat(location)

                logger.spam(f"Read value {val}")
                return val

    def get_absolute_location(self, addr: str, mode):
        logger.comp_func(f"calling get_absolute_location with args {addr} {mode}")
        location: int

        if mode == RelativeMode:
            location = self.inst_ptr + int(addr)

        elif mode == AbsoluteMode:
            location = int(addr)

        return location

    def cast_type(self, value, type_to_cast):
        logger.comp_func(f"cast {value} {type_to_cast}")
        if type(value) == str:
            value = str(value)
            if value.startswith("*"):
                logger.spam("recasting value of reg")
                assert self.regs.is_register(value[1:])
                read_value = self.read_addr(value[1:], AbsoluteMode)
                logger.spam(f"read value {read_value} from reg, now casting to {type_to_cast}")
                return self.cast_type(read_value, type_to_cast)#abs mode because it dosent matter, its a register

        match type_to_cast:
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
                raise ValueError(f"unknown type {type_to_cast}")

    def parse_mode(self, mode_str):
        """
        parse a mode string to a mode class
        """
        logger.spam(f"calling parse_mode with {mode_str}")
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
        logger.spam(f"Calling parse_opcode with args {inst_str}")
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
            
            case ins.StoreStringIndex.name:
                return ins.StoreStringIndex
            
            case ins.StoreStringLen.name:
                return ins.StoreStringLen

            case _:
                return False