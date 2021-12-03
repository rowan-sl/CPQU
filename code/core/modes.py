class Mode:
    """
    Mode of the argument thing
    """
    name: str

class RelativeMode(Mode):
    """
    Read things relative to the instruction_pointer
    """
    name = "mrel"

class AbsoluteMode(Mode):
    """
    Read things by there absolute memory adress
    """
    name = "mabs"