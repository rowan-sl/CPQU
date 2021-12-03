import re
import sys
from errors.core_errors import AddressError
from core.null import Null

class Registers:
    def __init__(self, computer) -> None:
        self.computer = computer
        self.regs = {}
    
    @staticmethod
    def is_register(name):
        if name in [
            "out",
            "ins",
            "tru",
            "fal",
            "nul",
        ]:
            return True

        elif re.match(r"r[a-z][a-z]", name) is not None:
            return True

        return False

    def write(self, reg, val):
        assert self.is_register(reg)
        match reg:
            case "out":
                print("stdout:", val)
            case "ins":
                pass
            case "tru":
                pass
            case "fal":
                pass
            case "nul":
                pass
            case _:
                #anything else
                if re.match(r"r[a-z][a-z]", reg) is not None:
                    #its a register
                    self.regs[reg] = val
                else:
                    raise ValueError("not a register!")

    def read(self, reg):
        assert self.is_register(reg)
        match reg:
            case "out":
                return AddressError
            case "ins":
                return self.computer.inst_ptr
            case "tru":
                return AddressError
            case "fal":
                return AddressError
            case "nul":
                return Null
            case _:
                #anything else
                if re.match(r"r[a-z][a-z]", reg) is not None:
                    #its a register
                    if reg in self.regs.keys():
                        return self.regs[reg]
                    else:
                        return Null
                else:
                    raise ValueError("not a register!")