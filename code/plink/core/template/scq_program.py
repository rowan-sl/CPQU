import datetime
from core.projinfo import version


class SCQProgram:
    instructions: list
    plink_ver: str
    author: str
    date: str

    def __init__(
        self,
        instructions: list,
        author: str="unspecified",
        plink_ver: str=version,
        date: datetime.date=None
    ) -> None:
        if date is not None:
            self.date = str(date)
        else:
            self.date = str(datetime.date.today())
        self.author = author
        self.plink_ver = plink_ver
        self.instructions = instructions