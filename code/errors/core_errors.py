import sys

class ComputerError(Exception):
    """
    Base class for all Computer related errors
    """

class UnstoppableComputerException(ComputerError):
    """
    Unkillable, Untouchable, Unstoppable, you know it, you love it, sys.exit()
    """
    def __init__(self, *args: object, **kwdargs: object) -> None:
        super().__init__(*args)
        sys.exit(1)

class SegmentionFault(UnstoppableComputerException):
    """
    (Core Dumped). This means that something tried to read or write where it shouldent have
    """