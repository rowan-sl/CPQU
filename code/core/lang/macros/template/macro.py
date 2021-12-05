class Macro:
    """
    Definition of a macro.
    macros are expanded after parsing, but before expanding addresses
    """
    def is_relevant(self, instruction) -> bool:
        """
        check if a instruction is relevant to this macro. shoud return false if not, and true if it is
        """

    def get_expanded(self) -> list:
        """
        Get expanded verison of the macro as a list of instructions.
        """