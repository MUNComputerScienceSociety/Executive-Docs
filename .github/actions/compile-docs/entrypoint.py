from typing import List

from pprint import pprint

import pathlib
import subprocess

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
minute_files: List[pathlib.Path] = list(pathlib.Path("./Minutes/").glob("*.md"))
print(minute_files)
output_path = pathlib.Path("/output")

years = {}

for file_ in minute_files:
    _, month_number, __, year = file_.stem.split("_")
    if year not in years:
        years[year] = {}
    month = MONTHS[int(month_number) + 1]
    if month not in years[year]:
        years[year][month] = []
    years[year][month].append(file_)

pprint(years)
