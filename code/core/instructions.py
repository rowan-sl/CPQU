class Instruction:
    """
    base class for all instructions
    """

    name: str
    nargs: int
    reqires_mode: bool = False


class ExitProgram(Instruction):
    """
    Exits the program

    Useage: `hlt` (does not require <mode>!!!!!)
    """

    name = "hlt"
    nargs = 0
    requires_mode = False


class StoreTo(Instruction):
    """
    Takes a value, a type, and a address, and writes the value to that adress as that type.

    Supported types: `int`, `float`, `str`, `bool`

    Useage: `<mode> sto <value> <type> <addr>`
    """

    name = "sto"
    nargs = 3


class StoreInequality(Instruction):
    """
    Takes two arguments (addresses), a operator, and a addr,
    and writes `tru` (builtin type) to `addr` if `operator` evaluats to true for `arg1` and `arg2` otherwise writes `fal`

    Values must be in a register, or in memory.
    Values are cast to and compared as <type>
    
    Supported types: `int`, `float`, `str`, `bool`

    see types.InequalityType for a list of supported inequalities

    Useage: `<mode> sin <type> <arg1> <oper> <arg2> <addr>`
    """

    name = "sin"
    nargs = 5


class AddTo(Instruction):
    """
    adds the first two arguments and stores it in the third
    Values must be in a register, or in memory.

    Useage: `<mode> add <type> <arg1> <arg2> <arg3>`
    """

    name = "add"
    nargs = 4


class SubtractTo(Instruction):
    """
    subtracts the first two arguments and stores it in the third
    Values must be in a register, or in memory.

    Basicaly the same as `add`, but for subtraction

    Useage: `<mode> add <type> <arg1> <arg2> <arg3>`
    """

    name = "sub"
    nargs = 4


class MultiplyTo(Instruction):
    """
    multiplys the first two arguments and stores it in the third
    Values must be in a register, or in memory.

    Basicaly the same as `add`, but for multiplication

    Useage: `<mode> mlt <type> <arg1> <arg2> <arg3>`
    """

    name = "mlt"
    nargs = 4


class DevideoTo(Instruction):
    """
    multiplys the first two arguments and stores it in the third
    Values must be in a register, or in memory.

    Basicaly the same as `mlt`, but for devision

    Useage: `<mode> div <type> <arg1> <arg2> <arg3>`
    """

    name = "div"
    nargs = 4


class MoveTo(Instruction):
    """
    move a value at one address to another address
    Values must be in a register, or in memory.

    Useage: `<mode> mov <addr1> <addr2>`
    """

    name = "mov"
    nargs = 2


class MoveIfEqual(Instruction):
    """
    move a `addr1` to `addr2`, if `arg1` and `arg2` are equal.
    Values must be in registers, or in memory.

    This is basicaly a shortcut for `rel jeq <arg1> <arg2> 3 <mode> mov <addr1> <addr2>`

    Useage: `<mode> meq <arg1> <arg2> <addr1> <addr2>`
    """

    name = "meq"
    nargs = 4


class CopyTo(Instruction):
    """
    copy a value at one address to another address
    Values must be in a register, or in memory.

    Useage: `<mode> cpy <addr1> <addr2>`
    """

    name = "cpy"
    nargs = 2


class CopyIfEqual(Instruction):
    """
    copy the value at `addr1` to `addr2`, if `arg1` and `arg2` are equal.
    Values must be in registers, or in memory.

    This is basicaly a shortcut for `rel jeq <arg1> <arg2> 3 <mode> cpy <addr1> <addr2>`

    Useage: `<mode> ceq <arg1> <arg2> <addr1> <addr2>`
    """

    name = "ceq"
    nargs = 4


class JumpIfEqual(Instruction):
    """
    jump if two values are equal.
    Values must be in registers, or in memory.

    Useage: `<mode> jeq <arg1> <arg2> <addr>`

    If `arg1` and `arg2` are found to be equal, then it jumps to `addr`
    """

    name = "jeq"
    nargs = 3


class JumpTo(Instruction):
    """
    Jump to `addr`.

    Useage: `<mode> jmp <addr>`
    """

    name = "jmp"
    nargs = 1
