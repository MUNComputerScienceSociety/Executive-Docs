import logging
import os
import pathlib
import subprocess
from typing import List

import click

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


def find_documents(input_path: pathlib.Path) -> List[pathlib.Path]:
    logger.info(f"Discovering documents within {input_path}...")
    document_files: List[pathlib.Path] = list(pathlib.Path(input_path).glob("*.md"))
    logger.info(f"{len(document_files)} documents found.")
    return document_files


def group_documents_by_year(document_files: List[pathlib.Path]):
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
    return years


def run_pandoc_on_document(input_path: pathlib.Path, output_path: pathlib.Path):
    logger.info(f"Building {input_path.name} (output path {output_path})")
    subprocess.run(
        [
            "pandoc",
            str(input_path),
            "-f",
            "markdown",
            "-t",
            "latex",
            "-s",
            "-o",
            output_path,
        ]
    )


@click.command()
@click.option("-i", "--input", "input_path_string", type=click.Path(exists=True), required=True)
@click.option("-o", "--output", "output_path_string", type=click.Path(exists=True), required=True)
def build_docs(input_path_string, output_path_string):
    input_path = pathlib.Path(input_path_string)
    output_path = pathlib.Path(output_path_string)

    document_files = find_documents(input_path)
    years = group_documents_by_year(document_files)

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

                run_pandoc_on_document(file_path, file_output_path)


if __name__ == "__main__":
    build_docs()
