import re
import sys
from errors.core_errors import AddressError
from core.null import Null
from collections import deque

class Registers:
    def __init__(self, computer, debug_io) -> None:
        self.dbg_io = debug_io
        self.computer = computer
        self.regs = {}
        self.syscall_regs = {
            "syscl.id": Null,
            "syscl.a1": Null,
            "syscl.a2": Null,
            "syscl.a3": Null,
        }
        self.syscall_results = deque()

    def add_syscall_res(self, results: list):
        self.syscall_results.extend(results)

    def clear_syscall_regs(self):
        self.syscall_regs = {
            "syscl.id": Null,
            "syscl.a1": Null,
            "syscl.a2": Null,
            "syscl.a3": Null,
        }

    def clear_syscall_res(self):
        self.syscall_results.clear()

    def reset(self):
        """
        Resets all registers
        """
        self.clear_syscall_regs()
        self.clear_syscall_res()
        self.regs = {}

    @staticmethod
    def is_register(name):
        if name in [
            "std",
            "ins",
            "tru",
            "fal",
            "nul",
            #syscall registers
            "syscl.id",
            "syscl.a1",
            "syscl.a2",
            "syscl.a3",
            "syscl.res"
        ]:
            return True

        elif re.match(r"r[a-z][a-z]", name) is not None:
            return True

        return False

    def write(self, reg, val):
        assert self.is_register(reg)
        if self.dbg_io:print(f"writing {val} to register {reg}")
        match reg:
            case "std":
                print(f"stdout ({type(val)}):", val)
            case "ins":
                pass
            case "tru":
                pass
            case "fal":
                pass
            case "nul":
                pass
            case r if r in [
            "syscl.id",
            "syscl.a1",
            "syscl.a2",
            "syscl.a3",
            "syscl.res"]:
                match reg:
                    case "syscl.res":
                        pass
                    case _:
                        self.syscall_regs[reg] = val
            case _:
                #anything else
                if re.match(r"r[a-z][a-z]", reg) is not None:
                    #its a register
                    self.regs[reg] = val
                else:
                    raise ValueError("not a register!")

    def read(self, reg):
        assert self.is_register(reg)
        if self.dbg_io:print(f"read from register {reg}")
        match reg:
            case "std":
                return input()
            case "ins":
                return self.computer.inst_ptr
            case "tru":
                return True
            case "fal":
                return False
            case "nul":
                return Null
            case r if r in [
            "syscl.id",
            "syscl.a1",
            "syscl.a2",
            "syscl.a3",
            "syscl.res"]:
                match reg:
                    case "syscl.res":
                        if len(self.syscall_results) != 0:
                            return self.syscall_results.popleft()
                        else:
                            return Null
                    case _:
                        return self.syscall_regs[reg]

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