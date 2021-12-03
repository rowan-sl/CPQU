from typing import List
import sys

import core.mess_with_pythonpath

from core.registers import Registers
from errors.core_errors import SegmentionFault, BadInstruction
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

    *Each instruction has a mode before it (ex: <mode> <instruction>), which controlls how arguments are read from registers.
    *A mode of abs means that it is the absolute index in memory, and a mode of rel means the relative position to the instruction pointer

    *The processor also has 52 data registers, denoted by r<register code> where register code is any two letters (a-z), and a few special ones, including:
    *out: the standard output. what is written to it will be outputted
    *ins: the instruction pointer
    *tru: a value of true
    *fal: a value of false
    *nul: null value, also behaves like /dev/null

    *each register and all memory not used by the program is initialized to Null.

    *It has a infinite memory size (at least not limited by the language),
    *although it must be allocated by the program to use it.

    """
    def __init__(self, program: List[str] | str) -> None:
        if type(program) == str:
            program_opcodes = self.basic_parse_program(program)
        else:
            program_opcodes = program
        self.inst_ptr = 0
        self.mem = Memory(program_opcodes)
        self.regs = Registers()

    def do_next_step(self):
        """
        Advance the computer to the next step, doing all processing for that step and updating all variables.
        """

        #~ get the next mode
        active_mode_string = self.mem.rat(self.inst_ptr)
        self.inst_ptr += 1
        active_mode = self.parse_mode(active_mode_string)

        if active_mode is False:
            raise BadInstruction(f"Encountered non-mode string {active_mode_string} at {self.inst_ptr}!!")
        if active_mode is True:
            print(f"program reached opcode `hlt` at addr {self.inst_ptr-1}, exiting gracefully!")
            sys.exit(0)

        #~ get the next opcode
        active_inst_string = self.mem.rat(self.inst_ptr)
        self.inst_ptr += 1
        active_inst = self.parse_opcode(active_inst_string)
        if active_inst is False:
            raise BadInstruction(f"Encountered non-instruction {active_inst_string} at {self.inst_ptr}!!")

        #~ read the instruction's args
        args = []

        for i in range(active_inst.nargs):
            # print(self.mem.mem)
            # print(self.inst_ptr, self.mem.rat(self.inst_ptr))
            args.append(self.mem.rat(self.inst_ptr))
            self.inst_ptr += 1

        # print(active_inst.__name__, args)

        #~ do a thing with that
        match active_inst:
            case ins.StoreTo:
                value_as_read = args[0]
                type = args[1]
                location_as_read = args[2]

                if Registers.is_register(location_as_read):
                    self.regs.write(location_as_read, self.cast_type(value_as_read, type))

                else:
                    location: int

                    if active_mode == RelativeMode:
                        location = self.inst_ptr + int(location_as_read)

                    elif active_mode == AbsoluteMode:
                        location = int(location_as_read)

                    self.mem.wat(self.cast_type(value_as_read, type), location)

            case _:
                print("unknown instruction!")

    def cast_type(self, value, type):
        match type:
            case "str":
                return str(value)
            case "int":
                return int(value)
            case "float":
                return float(value)
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

            case ins.JumpIfEqual.name:
                return ins.JumpIfEqual

            case ins.JumpTo.name:
                return ins.JumpTo

            case _:
                return False

    def basic_parse_program(self, program: str) -> List[str]:
        """
        Basic parsing of the program into operations
        """
        dirty_codes = []
        [dirty_codes.extend(code) for code in [[opcode.strip() for opcode in line_opcodes] for line_opcodes in [line.split(" ") for line in program.splitlines()]]]

        codes = []
        [codes.append(code) for code in dirty_codes if code not in [""]]
        return codes

program = [
    "rel", "sto", "Hello World!", "str", "out",
    "hlt",
]

computer = CPQUProcessor(program)

print(computer.mem.mem)

while True:
    computer.do_next_step()
