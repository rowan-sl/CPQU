import core.mess_with_pythonpath

from core.registers import Registers
from errors.core_errors import SegmentionFault, BadInstruction
from core.null import Null
from core.memory import Memory
from core.comp_types import *
from core.instructions import *


class Processor:
    """
    A bad processor.

    features that are not implemented are makred with a *

    *On initialization, it takes a program (list of oprators) and writes it to its own memory, which the program can then use.

    *The processor has a instruction pointer, which points to the current instruction being run.
    *After a instruction is run, it increments the instruction pointer by (at least) 1, generaly by how many arguments it takes.
    *however, some instructions can make the pointer jump to a new location.

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
    def __init__(self, program: list) -> None:
        self.inst_ptr = 0
        self.mem = Memory(program)
        self.regs = Registers()

    def do_next_step(self):
        """
        Advance the computer to the next step, doing all processing for that step and updating all variables.
        """

        active_inst_string = self.mem.rat(self.inst_ptr)
        active_inst = self.parse_instruction_to_cls(active_inst_string)
        if active_inst is False:
            raise BadInstruction(f"Encountered non-instruction {active_inst_string} at {self.inst_ptr}!!")


    def parse_instruction_to_cls(self, inst_str):
        match inst_str:
            case ExitProgram.name:
                return ExitProgram

            case StoreTo.name:
                return StoreTo

            case StoreInequality.name:
                return StoreInequality

            case AddTo.name:
                return AddTo

            case SubtractTo.name:
                return SubtractTo

            case MultiplyTo.name:
                return MultiplyTo

            case DevideoTo.name:
                return DevideoTo

            case MoveTo.name:
                return MoveTo

            case MoveIfEqual.name:
                return MoveIfEqual

            case CopyTo.name:
                return CopyTo

            case CopyIfEqual.name:
                return CopyIfEqual

            case JumpIfEqual.name:
                return JumpIfEqual

            case JumpTo.name:
                return JumpTo

            case _:
                return False