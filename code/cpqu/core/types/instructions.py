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
    nargs = 1
    requires_mode = False


class Syscall(Instruction):
    """
    Performs a syscall, based on the arguments in the sycall registers
    """

    name = "syscall"
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


class CastTo(Instruction):
    """
    Casts the first instruction to `type` in place
    value must be in a register, or in memory

    Useage: `<mode> cst <arg1> <type>`

    Supported types: `int`, `float`, `str`, `bool`
    """

    name = "cst"
    nargs = 2


class AddTo(Instruction):
    """
    adds the first two arguments and stores it in the third
    Values must be in a register, or in memory.

    Type: args are cast to type before they are added

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

    Casts each argument to its respective type, usefull for multiplying strings

    Useage: `<mode> mlt <type1> <arg1> <type2> <arg2> <arg3>`
    """

    name = "mlt"
    nargs = 5


class DevideoTo(Instruction):
    """
    devides the first two arguments and stores it in the third
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


class JumpIfTrue(Instruction):
    """
    jump if two values are equal.
    Values must be in registers, or in memory.

    Useage: `<mode> jit <arg1> <addr>`

    arg1 must be a register, or in memory

    If `arg1` is found to be True (with cast), then it jumps to `addr`
    """

    name = "jit"
    nargs = 2


class JumpTo(Instruction):
    """
    Jump to `addr`.

    Useage: `<mode> jmp <addr>`
    """

    name = "jmp"
    nargs = 1

class StoreStringIndex(Instruction):
    """
    Store a value from a string index

    Useage: `<mode> ssi <string> <index> <result_addr>
    """

    name = "ssi"
    nargs = 3

class StoreStringLen(Instruction):
    """
    Stores the length of the first argument to the second
    
    Useage: `<mode> ssl <string> <output>
    """
    
    name = "ssl"
    nargs = 2
