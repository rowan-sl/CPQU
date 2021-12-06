import argparse
import pathlib
import sys

from core.projinfo import name, description, version_prefix, version
from core.logging_config import logging_levels

from core.cli.actions import create_actions_subcommand

parser = argparse.ArgumentParser(prog=name,description=description)

create_actions_subcommand(parser)

parser.add_argument(
    "--version",
    dest="version",
    action="store_const",
    const=True,
    default=False,
    help="Display version and exit",
    required=False,
)

parser.add_argument(
    '-v',
    '--verbose',
    type=int,
    #TODO implement logging and verbosity
    help="""verbosity. table of settings: IT IS HIGHLY RECOMMENDED TO SET A VALUE OF 4 OR MORE!!
    01 logging.CRITICAL
    02 logging.ERROR
    03 logging.WARNING
    04 PROGRAM_STDOUT
    05 PROGRAM_STATE_LEVEL
    06 logging.INFO          (DEFAULT)
    07 PROGRAM_STARTUP_LEVEL
    08 INSTRUCTION_CALL_LEVEL
    09 INSTRUCTION_TRACE_LEVEL
    10 MEMORY_TRACE_LEVEL
    11 COMP_FUNC_LEVEL
    12 logging.DEBUG
    13 SPAMMER_LEVEL
    """,
    default=6
)

parser.add_argument(
    "-l",
    "--log-file",
    dest="logfile",
    metavar="LOGFILE",
    type=pathlib.Path,
    default=False,
    help="don't log to STDOUT, log to <file>",
)

args = parser.parse_args()

if args.version:
    print(version_prefix+version)
    exit(0)

if args.verbose > len(logging_levels):
    print(f"{args.verbose}? thats too much to ask")
    exit(0)