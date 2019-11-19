from typing import List

from pprint import pprint

import pathlib
import subprocess
import shlex
import logging

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

logger = logging.getLogger("Doc Builder")

logger.info("Discovering meeting minutes...")
minute_files: List[pathlib.Path] = list(pathlib.Path("./Minutes/").glob("*.md"))
logger.info(f"{len(minute_files)} meeting minutes found.")
output_path = pathlib.Path("/output")

years = {}

logger.info("Grouping minutes...")
for file_ in minute_files:
    if file_.stem == "Minutes_TEMPLATE":
        continue
    _, month_number, __, year = file_.stem.split("_")
    if year not in years:
        years[year] = {}
    month = MONTHS[int(month_number) - 1]
    if month not in years[year]:
        years[year][month] = []
    years[year][month].append(file_)
logger.info(
    f"Minutes grouped. {sum([len(year.keys()) for year in years.values()])} unique year/month combos found."
)

for year, months in years.items():
    year_path = output_path / year
    logger.info(f"Building meeting minutes for {year} (output path {year_path})")

    for month, files in months.items():
        month_path = year_path / month
        logger.info(
            f"Building meeting minutes for {month} {year} (output path {month_path})"
        )
        month_path.mkdir(parents=True, exist_ok=True)

        for file_path in files:
            file_output_path = str(month_path / (file_path.stem + ".pdf"))
            logger.info(f"Building {file_path.name} (output path {file_output_path})")
            subprocess.run(
                [
                    "pandoc",
                    str(file_path),
                    "-f",
                    "markdown",
                    "-t",
                    "pdf",
                    "-s",
                    "-o",
                    file_output_path,
                ]
            )

pprint(years)
