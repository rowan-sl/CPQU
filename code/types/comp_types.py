from typing import Any

from registers import Registers


class Null:
    "v o i d"


class BaseCompType:
    """
    base class for computer all types
    """

    # a list of possible values, none if it does not specify spacific possiblities
    values: list | None

    # the value of the type. set when class is initialized
    value: Any


class Address(BaseCompType):
    """
    A adress of a thing (including registers). int if it is a address, str if it is a register
    """

    values = None

    def __init__(self, value):
        try:
            val = int(value)
            self.is_register = False
            self.value = val
        except:
            pass
        if Registers.is_register(value):
            self.is_register = True
            self.value = value
            return
        raise ValueError("value must be a int, or a register name!")


class InequalityType(BaseCompType):
    """
    Various inequality operators.

    supported operators:
    `ltn` (less than),
    `gtn` (greater than),
    `leq` (less than or equal to),
    `geq` (greater than or equal to),
    `neq` (not equal to),
    `eqt` (equal to),
    """

    values = [
        "ltn",
        "gtn",
        "leq",
        "geq",
        "neq",
        "eqt",
    ]

    def __init__(self, value) -> None:
        assert value in self.values
        self.value = value
