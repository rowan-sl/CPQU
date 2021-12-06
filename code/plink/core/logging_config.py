import logging

# & info logger level is 20, debug is 10
PROGRAM_STDOUT = 22  # used for normal program output
PROGRAM_STATE_LEVEL = 21  # info about where the program is (exited with code, )
PROGRAM_STARTUP_LEVEL = 19  # debug info, just about program startup
INSTRUCTION_CALL_LEVEL = 16  # just print info about what instruction is being called
INSTRUCTION_TRACE_LEVEL = 15  # print info about what the instruction is doing
MEMORY_TRACE_LEVEL = 14  # log reads and writes to memory
COMP_FUNC_LEVEL = 13  # log calling of buitin functions

SPAMMER_LEVEL = 9  # lower than debug, can spam logs even worse than any other level

logging_levels = [
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    PROGRAM_STDOUT,
    PROGRAM_STATE_LEVEL,
    logging.INFO,
    PROGRAM_STARTUP_LEVEL,
    INSTRUCTION_CALL_LEVEL,
    INSTRUCTION_TRACE_LEVEL,
    MEMORY_TRACE_LEVEL,
    COMP_FUNC_LEVEL,
    logging.DEBUG,
    SPAMMER_LEVEL,
    # logging.NOTSET,
]
level_names = {
    logging.CRITICAL: "logging.CRITICAL",
    logging.ERROR: "logging.ERROR",
    logging.WARNING: "logging.WARNING",
    PROGRAM_STDOUT: "PROGRAM_STDOUT",
    PROGRAM_STATE_LEVEL: "PROGRAM_STATE_LEVEL",
    logging.INFO: "logging.INFO",
    PROGRAM_STARTUP_LEVEL: "PROGRAM_STARTUP_LEVEL",
    INSTRUCTION_CALL_LEVEL: "INSTRUCTION_CALL_LEVEL",
    INSTRUCTION_TRACE_LEVEL: "INSTRUCTION_TRACE_LEVEL",
    MEMORY_TRACE_LEVEL: "MEMORY_TRACE_LEVEL",
    COMP_FUNC_LEVEL: "COMP_FUNC_LEVEL",
    logging.DEBUG: "logging.DEBUG",
    SPAMMER_LEVEL: "SPAMMER_LEVEL",
    # logging.NOTSET,
}


def get_logger_level(verbosity: int) -> int:
    assert verbosity <= len(logging_levels)
    return logging_levels[verbosity-1]


def get_level_name(level: int) -> str:
    return level_names[level]


def create_log_level(name: str, level: int):
    logging.addLevelName(level, name)

    def custom_log_fn(self, message, *args, **kws):
        if self.isEnabledFor(level):
            # Yes, logger takes its '*args' as 'args'.
            self._log(level, message, args, **kws)

    return custom_log_fn


def configure_loggers():
    logging.Logger.program_stdout = create_log_level("PRGRM_STDOUT", PROGRAM_STDOUT)
    logging.Logger.program_state = create_log_level("PRGRM_STATE", PROGRAM_STATE_LEVEL)
    logging.Logger.program_startup = create_log_level("PRGRM_STARTUP", PROGRAM_STARTUP_LEVEL)
    logging.Logger.inst_call = create_log_level("INST_CALL", INSTRUCTION_CALL_LEVEL)
    logging.Logger.inst_trace = create_log_level("INST_TRACE", INSTRUCTION_TRACE_LEVEL)
    logging.Logger.mem_trace = create_log_level("MEM_TRACE", MEMORY_TRACE_LEVEL)
    logging.Logger.comp_func = create_log_level("COMP_FUNC", COMP_FUNC_LEVEL)
    logging.Logger.spam = create_log_level("SPAM", SPAMMER_LEVEL)


def init_logging(log_level: int, filename: str=None):
    configure_loggers()
    fmt: str
    if log_level > SPAMMER_LEVEL:
        fmt = "[%(module)s][%(name)s][%(levelname)s@%(asctime)s] :: %(message)s"
        datefmt = '%d::%S:%M:%H'#realisticaly, this wouldent run for more than one day
    else:
        #& Behold, le MONSTROSITY!
        fmt = "[%(levelname)s][%(asctime)s]-->[%(filename)s][%(funcName)s]@[%(lineno)d] by [%(name)s] in [%(processName)s][%(threadName)s]\n--->>> %(message)s\n"
        datefmt = '%d/%m/%y::%S:%M:%H'#whie not
    if filename is not None:
        logging.basicConfig(
            filename=filename,
            datefmt=datefmt,
            format=fmt,
            encoding="utf-8",
            level=log_level
        )
    else:
        logging.basicConfig(
            format=fmt,
            datefmt=datefmt,
            encoding="utf-8",
            level=log_level
        )
