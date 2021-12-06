import pathlib
import sys

sys.path.extend(
    [
        str(pathlib.Path(__file__).parents[1]),#CPQU directory
        str(pathlib.Path(__file__).parents[2]),#code directory
    ]
)