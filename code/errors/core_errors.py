import sys


class ComputerError(Exception):
    """
    Base class for all Computer related errors
    """


class SegmentionFault(ComputerError):
    """
    (Core Dumped). This means that something tried to read or write where it shouldent have
    """

    def __init__(self, *args: object, **kwdargs: object) -> None:
        print("Segmentation Fault")
        print("(core dumped)")
        super().__init__(*args, **kwdargs)

class BadInstruction(ComputerError):
    """
    Encountered a instruction it dosent know what to do with
    """
