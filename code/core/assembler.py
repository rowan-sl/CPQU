from typing import (
    List
)
import re


class Assembler:
    def __init__(self) -> None:
        pass

    def assemble(self, program):
        """
        Does all necessary preprocessing/parsing of a program to turn it into bare instructions for the processor
        """
        parsed_prog = self.parse_program(program)
        expand_prog = self.expand_macros(parsed_prog)
        expand_addr = self.expand_addresses(expand_prog)
        return expand_addr

    def expand_addresses(self, program: List[str]):
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

    def expand_macros(self, program: List[str]):
        """
        Expands macros into there full definition
        """
        parsed_prog = []

        #index of current opcode in program
        index = 0
        while index < len(program):
            orig_opcode = program[index]
            #do not increment the index at the end of the loop
            no_auto_index = False

            match orig_opcode:
                case "end":
                    #exit with code 0 (sucsess)
                    #! this is worth two instructions!
                    parsed_prog.extend(["hlt", "0"])

                case "fail":
                    #exit with code 1 (error)
                    #! this is worth two instructions!
                    parsed_prog.extend(["hlt", "1"])

                case match if re.search(f"fail<.+?>", orig_opcode) is not None:
                    reason = match.removeprefix("fail<").removesuffix(">")
                    parsed_prog.extend(["sto", "Program error: \""+reason+"\"", "str", "std", "hlt", "0"])

                case _:
                    parsed_prog.append(orig_opcode)

            if not no_auto_index:
                index += 1

        return parsed_prog

    def parse_program(self, program: str) -> List[str]:
        """
        Parsing of the program into opcodes
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