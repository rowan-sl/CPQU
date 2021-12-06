#! you must not have any files in code/CPQU/core that have the same name as code/Plink/core

#& package imports
import sys
import pathlib as pl
import logging
from dill import dumps, loads

#& hehe
import core.plink_mess_with_pythonpath

#&program info
from core.projinfo import version, version_prefix

#& argsparsing
from core.cli.argsparsing import args

#& initialize logging
from core.logging_config import (
    get_level_name,
    get_logger_level,
    init_logging,
)

level = get_logger_level(args.verbose)
init_logging(level, args.logfile)
mlogger = logging.getLogger("MAIN")
mlogger.critical(f"Initialized logging at level {get_level_name(level)}")
mlogger.critical(f"{version_prefix}{version}")
mlogger.critical(f"Pling is starting...")

#& CPQU imports
from cpqu.processor import CPQUProcessor
from cpqu.core.lang.assembler import Assembler

#macros
from cpqu.core.lang.macros.end_fail_macro import EndMacro, FailMacro
from cpqu.core.lang.macros.print_macro import PrintMacro
macro_list = [
    EndMacro,
    FailMacro,
    PrintMacro,
]

mlogger.info(f"Args: {args}")

debug = False#! REMOVE THIS AND REPLACE w/ LOGGER

try:
    if args.run_file is not None:
        rfile: pl.Path = args.run_file
        assert rfile.exists()
        mlogger.info(f"running {rfile}")
        processor = CPQUProcessor()
        file_content: str | list
        compiled: bool
        if args.is_assembled == "n":
            file_content = rfile.read_text()
            compiled = False
        elif args.is_assembled == "y":
            file_bytes = rfile.read_bytes()
            compiled = True
            try:
                file_content = loads(file_bytes)
            except BaseException as e:
                print("A error occured while decoding the file. are you shure it is a assembled file?")
                if debug:
                    print(e)
                sys.exit(1)
        else:
            if debug:
                print("interpreting file type")
            if "." not in rfile.name:
                print("File does not have a extension! you must specify the --is-assembled argument")
                sys.exit(1)
            extension = rfile.name.split(".")[-1]
            match extension:
                case "scq":
                    file_content = rfile.read_text()
                    compiled = False
                case "cscq":
                    file_bytes = rfile.read_bytes()
                    compiled = True
                    try:
                        file_content = loads(file_bytes)
                    except BaseException as e:
                        print("A error occured while decoding the file. are you shure it is a assembled file?")
                        if debug:
                            print(e)
                        sys.exit(1)
                case _:
                    print(f"unknown file extension {extension} for StringCodeQ file! you must specify the --is-assembled argument")
                    sys.exit(1)
        processor.load_program(file_content, compiled)
        processor.run_till_done()
except AttributeError as e:
    pass
try:
    if args.assemble_file is not None:
        print("assembling:", args.assemble_file)
except AttributeError as e:
    pass
