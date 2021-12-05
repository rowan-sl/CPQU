from core.null import Null
from errors.core_errors import SegmentionFault


class Memory:
    """
    errr... a class to represent memory. provides usefull functions to deal with the memory.
    """

    def __init__(self, mem: list, dbg_io) -> None:
        self.dbg_io = dbg_io
        self.mem = mem
        self.shrink_wrap()

    def reset(self):
        """
        Clears and resets the memory
        """
        self.mem = []

    def load_memory(self, mem: list):
        """
        Resets and loads `mem` into memory
        """
        self.reset()
        self.mem.extend(mem)

    def get_precentage_used(self) -> float:
        """
        Returns the percentage of memory used (not null)
        """
        num_of_null = self.mem.count(Null)
        total = len(self.mem)
        perc_str = str(total/num_of_null)
        dec_index = perc_str.index(".")
        return float(perc_str[0:dec_index+3])

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
        if self.dbg_io:print(f"writing {val} to {adr}")
        """
        Writes val to adr.
        If adr is larger than the maximum address in memory, raises SegmentationFault
        """
        if adr > self.size():
            # & oopsie whoopsise poopsise you messed up
            raise SegmentionFault(
                f"Cannot set `{val}` at `{adr}`, as `{adr}` is farther than the maximun adress ({self.size()})!!"
            )

        elif adr < 0:
            # & what did you expect
            raise ValueError("adr cannot be less than 0!")

        else:
            # print("prev mem\n", self.mem)
            self.mem[adr] = val
            # print("modified mem\n", self.mem)


    def rat(self, adr):
        """
        Reads and returns the value at adr.
        If adr is not in mem, raises SegmentationFault
        """
        if adr > self.size():
            # & oopsie whoopsise poopsise you messed up
            raise SegmentionFault(
                f"Cannot read value at address {adr}, as {adr} is farther than the maximun address ({self.size()})!!"
            )

        elif adr < 0:
            # & what did you expect
            raise ValueError("adr cannot be less than 0!")

        else:
            if self.dbg_io:print(f"reading value {self.mem[adr]} from {adr}")
            return self.mem[adr]

    def size(self):
        """
        returns largest address that can be written to in memory
        """
        return len(self.mem) - 1