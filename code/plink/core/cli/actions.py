import argparse
import pathlib as pl


def create_actions_subcommand(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="actions", description="Plink action subcommands"
    )

    subcommand_run = subparsers.add_parser(
        "run",
        help="run a SCQ or compiled SCQ program, by default, weather or not the file needs assembling will be determined by its extension (.scq vs .cscq). if this is undesierable, pleas use the --is-assembled argument",
    )

    subcommand_run.add_argument(
        "run_file",
        metavar="FILE",
        default=None,
        type=pl.Path,
        help="SCQ file to run",
    )

    subcommand_run.add_argument(
        "--is-assembled",
        dest="is_assembled",
        choices=["y", "n"],
        help="specify if the input file requires assembling",
        required=False,
    )

    subcommand_assemble = subparsers.add_parser(
        "assemble", help="assemble a SCQ program to a compiled version"
    )

    subcommand_assemble.add_argument(
        "assemble_file",
        default=None,
        metavar="FILE",
        type=pl.Path,
        help="SCQ file to assemble",
    )
    
    subcommand_assemble.add_argument(
        "--write-text",
        dest='write_text',
        action='store_const',
        const=True,
        default=False,
        help="Write stringified version of assembled instructions to file insead of normal output. cannot be loaded or ran",
        required=False,
    )

    subcommand_assemble.add_argument(
        "-o",
        dest="output_file",
        metavar="FILE",
        type=pl.Path,
        default=False,
        help="file to write the complied result to. by default it is the source file with the .cscq extension",
        required=False,
    )
