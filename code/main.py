from types.registers import *
from errors.core_errors import *
from types.comp_types import *
from types.instructions import *


class Memory:
    """
    errr... a class to represent memory. provides usefull functions to deal with the memory.
    """

    def __init__(self, mem: list) -> None:
        self.mem = []
        for idx, val in enumerate(mem):
            self.wat(val, idx)

    def enlarge(self, ammount):
        """
        Increases the memory's size by ammount, initializing it to Null
        """
        assert ammount > 0
        self.mem += [Null] * ammount

    def enlarge_to(self, addr):
        """
        extends the memorys size so that the max adress is addr
        """
        current_max = self.size()
        self.enlarge(addr - current_max)

    def shrink_wrap(self):
        """
        Remove all Null memory at the end of memory, reducing to size 0 if necessary.
        Returns the number of values removed
        """
        removed = 0
        while True:
            if len(self.mem) == 0:
                # nothing can be removed
                return removed

            if self.mem[-1] == Null:
                # remove the null
                del self.mem[-1]
                # count it
                removed += 1

            else:
                # not a null value, return
                return removed

    def reset(self):
        """
        Reset the memory, also sets size to 0
        """
        self.mem.clear()

    def wat(self, val, adr):
        """
        Writes val to adr.
        If adr is larger than the maximum address in memory, raises SegmentationFault
        """
        if adr > self.size():
            # & oopsie whoopsise poopsise you messed up
            raise SegmentionFault(
                f"Cannot set {val} at {adr}, as {adr} is larger than the maximun adress ({self.size()})!!"
            )

        elif adr < 0:
            # & what did you expect
            raise ValueError("adr cannot be less than 0!")

        else:
            self.mem[adr] = val

    def rat(self, adr):
        """
        Reads and returns the value at adr.
        If adr is not in mem, raises SegmentationFault
        """
        if adr > self.size():
            # & oopsie whoopsise poopsise you messed up
            raise SegmentionFault(
                f"Cannot read value from {adr}, as {adr} is larger than the maximun adress ({self.size()})!!"
            )

        elif adr < 0:
            # & what did you expect
            raise ValueError("adr cannot be less than 0!")

        else:
            return self.mem[adr]

    def size(self):
        """
        returns largest address that can be written to in memory
        """
        return len(self.mem) - 1


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
        self.mem = Memory(program)
        self.regs = Registers()