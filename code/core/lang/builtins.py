import builtins
from typing import List, Union


class Builtins:
    def __init__(self) -> None:
        self.builtins_list = [
            "ltn",
            "gtn",
            "leq",
            "geq",
            "neq",
            "eqt",
            "sto",
            "sin",
            "add",
            "sub",
            "mlt",
            "div",
            "mov",
            "meq",
            "cpy",
            "ceq",
            "cst",
            "ssi",
            "ssl",
            "str",
            "float",
            "int",
            "bool",
            "syscl.id",
            "syscl.a1",
            "syscl.a2",
            "syscl.a3",
            "syscl.res",
            "std",
            "ins",
            "tru",
            "fal",
            "nul",
            "hlt",
            "mabs",
            "mrel",
            "jmp",
            "jit",
            "syscall",
            "nop",
            "define",
            "use",
            "end",
            "fail",
        ]

    def is_builtin(self, name: str):
        return name in self.builtins_list

    def register(self, name: Union[str, List[str]]):
        if type(name) == str:
            assert name not in self.builtins_list
            self.builtins_list.append(name)
        elif type(name) == list:
            for n in name:
                assert n not in self.builtins_list
            self.builtins_list.extend(name)

    def deregister(self, name: str):
        if name in self.builtins_list:
            del self.builtins_list[self.builtins_list.index(name)]

