import logging
import os
import pathlib
import subprocess
from typing import List

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
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
)

logger.info("Discovering documents...")
document_files: List[pathlib.Path] = list(pathlib.Path(os.getenv("INPUT_INPUT_PATH")).glob("*.md"))
logger.info(f"{len(document_files)} documents found.")
output_path = pathlib.Path(os.getenv("INPUT_OUTPUT_PATH"))

years = {}

logger.info("Grouping documents...")
for file_ in document_files:
    if file_.stem.endswith("_TEMPLATE"):
        continue
    _, month_number, __, year = file_.stem.split("_")
    if year not in years:
        years[year] = {}
    month = MONTHS[int(month_number) - 1]
    if month not in years[year]:
        years[year][month] = []
    years[year][month].append(file_)
logger.info(
    f"Documents grouped. {sum([len(year.keys()) for year in years.values()])} unique year/month combos found."
)

for year, months in years.items():
    year_path = output_path / year
    logger.info(f"Building documents for {year} (output path {year_path})")

    for month, files in months.items():
        month_path = year_path / month
        logger.info(
            f"Building documents for {month} {year} (output path {month_path})"
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
                    "latex",
                    "-s",
                    "-o",
                    file_output_path,
                ]
            )
