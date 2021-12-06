import pathlib as pl
import sys

sys.path.extend(
    [
        str(pl.Path(__file__).parents[1]),#Plink directory
        str(pl.Path(__file__).parents[2]),#code directory
        str(pl.Path(pl.Path(__file__).parents[2], "cpqu")),#CPQU directory
    ]
)