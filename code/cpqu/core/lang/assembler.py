from typing import (
    List
)
import re
from dataclasses import dataclass
import logging

from core.lang.macros.template.macro import Macro
from core.lang.builtins import Builtins

from uuid import uuid4

@dataclass
class DefineDefinition:
    """
    class to represent one definition of SCQ's define<>{} functionality.
    """
    name: str
    args: list[str]
    inner_code: list[str]

    def get_with_args_replaced(self, arg_values: list):
        """
        Return inner_code with args replaced with arg_values
        Arg_values a list of arguments, to be replaced in the order shown in the definition

        This relplaces all occurences of arg_name with arg_value
        """
        current_id = "id" + str(uuid4()).replace("-", "_")
        #TODO implement this
        res = []
        for inst in self.inner_code:
            if inst.startswith("%"):
                assert inst[1:] in self.args
                index = self.args.index(inst[1:])
                res.append(arg_values[index])
            else:
                #replace addresses with something unique
                if inst.startswith("@") or inst.startswith("$"):
                    pre = inst[0]
                    end = inst[1:]
                    res.append(pre + current_id + end)
                elif inst.startswith("*"):
                    #make shure its a ref
                    assert inst[1] == "$"
                    pre = inst[0]+inst[1]
                    end = inst[2:]
                    res.append(pre + current_id + end)
                else:
                    res.append(inst)
        return res

def split_respect_strings(string: str, split_on: str, keep_markers: bool = False) -> list[str]:
    """
    like split()
    but respects string markers (")
    so doing split_respect_strings("\"Test e\" asdf", " ") would give you ["Test e", "asdf"]
    """
    assert split_on != "\""
    assert split_on != "\'"
    res = ""
    segments = []
    in_block = False
    for char in string:
        if char == "\"":
            in_block = not in_block
            if keep_markers:
                res += "\""
        else:
            if char == split_on:
                if in_block:
                    res += char
                else:
                    segments.append(res)
                    res = ""
            else:
                res += char
    segments.append(res)
    return segments

llogger = logging.getLogger("ASMBLR")
class Assembler:
    """
    avengers...
    """
    def __init__(self, macros: List[Macro]) -> None:
        self.macros = macros

        self.define_definition_re_str = r"(define) +([a-zA-Z_][a-zA-Z_1234567890]*) *(<( *[a-zA-Z_][a-zA-Z_1234567890]* *,* *)*>) *{([^}]*)}"
        self.define_definition_re = re.compile(
            self.define_definition_re_str,
            re.MULTILINE,
        )

        self.defined_defines: list[DefineDefinition] = []
        self.defines_defined: bool = False
        self.builtins = Builtins()

    def assemble(self, program):
        """
        Does all necessary preprocessing/parsing of a program to turn it into bare instructions for the processor
        """
        llogger.debug("avengers...")

        comments_removed = self.remove_comments(program)

        llogger.debug("removed comments")
        llogger.spam(comments_removed)

        defines_removed = self.get_define_definitions(comments_removed)

        llogger.debug("Loaded define definitions")
        llogger.spam(defines_removed)

        parsed_prog = self.parse_program(defines_removed)

        llogger.debug("basic parsed program")
        llogger.spam(parsed_prog)

        defines_expanded = self.expand_defines(parsed_prog)

        llogger.debug("defines expanded")
        llogger.spam(defines_expanded)

        expand_prog = self.expand_macros(defines_expanded)

        llogger.debug("expand macros")
        llogger.spam(expand_prog)

        expand_addr = self.expand_addresses(expand_prog)

        llogger.debug("addr expanded")
        llogger.spam(expand_addr)

        markers_removed = self.remove_str_markers(expand_addr)

        llogger.debug("assemble")
        llogger.spam(markers_removed)
        llogger.debug("assembly done")

        return markers_removed

    def get_define_definitions(self, program: str) -> str:
        """
        Gets and stores all define definitons.
        returns the program without the definitions.
        """
        while True:
            latest_definition = re.search(self.define_definition_re, program)
            if latest_definition is None:
                break
            llogger.spam(latest_definition)
            llogger.spam(latest_definition.groups())

            define_name = latest_definition.group(2).strip()

            arg_names = [arg_t.strip() for arg_t in latest_definition.group(3).strip().removeprefix("<").removesuffix(">").strip().split(",")]

            for name in arg_names:
                assert not self.builtins.is_builtin(name)

            parsed_inner_code = self.parse_program(latest_definition.group(5))
            
            text_range = latest_definition.span()

            llogger.spam(f"Define info: \nName: {define_name}\nArgs: {arg_names}\nCode: {parsed_inner_code}\nRange {text_range}")

            define_def = DefineDefinition(define_name, arg_names, parsed_inner_code)
            
            for define in self.defined_defines:
                assert define_def.name != define.name

            self.defined_defines.append(define_def)
            
            llogger.spam(f"Program with define removed\n{program[:text_range[0]]+program[text_range[1]:]}")
            
            #& remove define from the program
            program = program[:text_range[0]]+program[text_range[1]:]

        llogger.spam(f"Defines:\n{self.defined_defines}")

        self.defines_defined = True
        
        return program

    def expand_defines(self, program: List[str]) -> List[str]:
        """
        Expands defines in program into the actual code. should take place after basic parsing.
        """
        #TODO implement this
        res = []
        for inst in program:
            if inst.startswith("!"):
                name, rest = inst.split("(", maxsplit=1)
                rest = rest[:-1]
                name = name[1:]
                args = [
                    a.strip()
                    for a in
                    split_respect_strings(rest, ",", True)
                ]
                llogger.spam(f"Define used: Original: {inst}, name: {name}, args: {args}")
                define = None
                for d in self.defined_defines:
                    if d.name == name:
                        define = d
                assert define is not False
                define_code = define.get_with_args_replaced(args)
                llogger.spam(f"Define with code replaced: {define_code}")
                res.extend(define_code)
            else:
                res.append(inst)
        return res

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
                codes.append(code[1:-1])
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
            
            elif orig_opcode.startswith("*"):
                #make shure that it is a reference, not definition
                assert orig_opcode[1] == "$"
                addr_name = orig_opcode[2:]
                if addr_name not in address_definitions.keys():
                    raise ValueError(f"address {addr_name} is referenced at index {index} but never defined!")

                parsed_prog.append("*" + str(address_definitions[addr_name]))

            elif orig_opcode.startswith("@"):
                parsed_prog.append("nop")

            else:
                parsed_prog.append(orig_opcode)

            if not no_auto_index:
                index += 1

        llogger.debug("addresses defined:")
        llogger.debug(address_definitions)
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
        in_string_block = False
        in_parens = False

        index = 0
        while True:
            next_char = program[index]
            # print(next_char)
            # print(in_string_block)
            if next_char == "\"":
                # print("entering/exiting string block")
                next_code += "\""
                in_string_block = not in_string_block
            elif ((next_char in ["(", ")"]) and (not in_string_block)):
                next_code += next_char
                if next_char == "(":
                    in_parens = True
                elif next_char == ")":
                    in_parens = False
            else:
                if ((next_char not in [" ", "\n"]) or (in_string_block or in_parens)):
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