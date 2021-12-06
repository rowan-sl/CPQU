from typing import (
    List
)
import re
from dataclasses import dataclass

from core.lang.macros.template.macro import Macro

@dataclass
class DefineDefinition:
    """
    class to represent one definition of SCQ's define<>{} functionality.
    """
    name: str
    args: list[str]
    inner_code: list[str]


class Assembler:
    """
    avengers...
    """
    def __init__(self, macros: List[Macro]) -> None:
        self.macros = macros
        # self.define_definition_re = re.compile(
        #     r"define ?[a-zA-Z_][a-zA-Z_1234567890]* <( *[a-zA-Z_][a-zA-Z_1234567890]* *,* *)*> *{[^}]*}",
        #     flags=re.MULTILINE,
        # )
        # self.define_definition_re_v2 = re.compile(
        #     r"(define) ?([a-zA-Z_][a-zA-Z_1234567890]*) (<( *[a-zA-Z_][a-zA-Z_1234567890]* *,* *)*>) *{([^}]*)}",
        #     re.MULTILINE,
        # )
        # self.define_definition_re_v3 = re.compile(
        #     r"(define) ?([a-zA-Z_][a-zA-Z_1234567890]*) (<( *[a-zA-Z_][a-zA-Z_1234567890]* *,* *)*>) *{",
        #     re.MULTILINE,
        # )#use a while loop to avoid getting the ending } wrong

    def assemble(self, program):
        """
        Does all necessary preprocessing/parsing of a program to turn it into bare instructions for the processor
        """
        print("avengers...")

        comments_removed = self.remove_comments(program)

        print("removed comments")
        print(comments_removed)

        parsed_prog = self.parse_program(comments_removed)

        print("basic parsed program")
        print(parsed_prog)

        expand_prog = self.expand_macros(parsed_prog)

        print("expand macros")
        print(expand_prog)

        expand_addr = self.expand_addresses(expand_prog)

        print("addr expanded")
        print(expand_addr)

        markers_removed = self.remove_str_markers(expand_addr)

        print("assemble")
        print(markers_removed)
        print("assembly done")

        return markers_removed

    def remove_comments(self, program: str) -> str:
        """
        removes all line comments from a program
        """
        return re.sub(r"#.*", "", program)#its that simple

    def remove_str_markers(self, program: List[str]) -> List[str]:
        """
        remove string markers, like `"` from the code. usefull to avoid things messing up confusing strings with other things in other
        steps of assembling. should be the last step in the assembly process.
        """
        codes = []
        for code in program:
            if (code.startswith("\"") and code.endswith("\"")):
                codes.append(code[1:-2])
            else:
                codes.append(code)
        return codes

    def expand_addresses(self, program: List[str]) -> List[str]:
        """
        Expands addresses, notated as `@name` (definition) and `$name` (reference),
        into their numeric representation.

        note that the name must consist of only alphabet letters, numbers, or underscords (matches the regex [a-zA-Z1234567890_])
        """
        parsed_prog = []

        address_definitions = {}

        #!find all adress definitions
        for i, val in enumerate(program):
            if val.startswith("@"):
                addr_name = val[1:]
                if addr_name in address_definitions.keys():
                    raise ValueError(f"address {addr_name} is defined at index {i} but it has already been defined!")

                address_definitions[addr_name] = i+1

        #index of current opcode in program
        index = 0
        #! dereference addresses
        while index < len(program):
            orig_opcode = program[index]
            #do not increment the index at the end of the loop
            no_auto_index = False

            if orig_opcode.startswith("$"):
                addr_name = orig_opcode[1:]
                if addr_name not in address_definitions.keys():
                    raise ValueError(f"address {addr_name} is referenced at index {index} but never defined!")

                parsed_prog.append(str(address_definitions[addr_name]))

            elif orig_opcode.startswith("@"):
                parsed_prog.append("nop")

            else:
                parsed_prog.append(orig_opcode)

            if not no_auto_index:
                index += 1

        print("addresses defined:")
        print(address_definitions)
        return parsed_prog

    def expand_macros(self, program: List[str]) -> List[str]:
        """
        Expands macros into there full definition
        """
        parsed_prog = []

        for opcode in program:
            for macro_cls in self.macros:
                macro: Macro = macro_cls()
                if macro.is_relevant(opcode):
                    parsed_prog.extend(macro.get_expanded())
                    del macro
                    break
                del macro
            else:
                parsed_prog.append(opcode)

        return parsed_prog

    def parse_program(self, program: str) -> List[str]:
        """
        Parsing of the program into opcodes
        """
        codes = []

        next_code = ""
        in_enclosing_block = False

        index = 0
        while True:
            next_char = program[index]
            # print(next_char)
            # print(in_enclosing_block)
            if next_char == "\"":
                # print("entering/exiting enclosing block")
                next_code += "\""
                in_enclosing_block = not in_enclosing_block
            else:
                if ((next_char not in [" ", "\n"]) or (in_enclosing_block)):
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