import re

from core.lang.macros.template.macro import Macro

class EndMacro(Macro):
    """
    End the program with exit code 0
    """
    def is_relevant(self, instruction) -> bool:
        if instruction == "end":
            return True

    def get_expanded(self) -> list:
        return ["hlt", "0"]

class FailMacro(Macro):
    """
    End the program with exit code 1,
    and (optionaly) with a error message
    """
    def __init__(self) -> None:
        self.expanded_instructions = []

    def is_relevant(self, instruction) -> bool:
        match instruction:
            case "fail":
                self.expanded_instructions = ["hlt", "1"]
                return True

            case match if re.search(r"fail<.+?>", instruction) is not None:
                reason = match.removeprefix("fail<").removesuffix(">")
                self.expanded_instructions = ["sto", "Program error: "+reason, "str", "std", "hlt", "1"]
                return True
            
            case _:
                return False
    
    def get_expanded(self) -> list:
        return self.expanded_instructions