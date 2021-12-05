import re

from core.lang.macros.template.macro import Macro

class PrintMacro(Macro):
    """
    Adds a print function macro
    """
    def __init__(self) -> None:
        self.expanded_instructions = []

    def is_relevant(self, instruction) -> bool:
        match = re.search(r"print<(.+?)>", instruction)
        if match is not None:
            value = match.group(0).removeprefix("print<").removesuffix(">").strip()
            self.expanded_instructions = ["sto", value, "str", "std"]
            return True
        return False
    
    def get_expanded(self) -> list:
        return self.expanded_instructions