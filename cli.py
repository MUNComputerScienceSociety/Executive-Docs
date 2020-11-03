import logging
import os
import pathlib
import subprocess
import json
from datetime import datetime
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

TODAY = datetime.now().strftime("%B %d, %Y")

logger = logging.getLogger("Doc Builder")
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
)


def find_documents(input_path: pathlib.Path) -> List[pathlib.Path]:
    logger.info(f"Discovering documents within {input_path}...")
    document_files: List[pathlib.Path] = list(
        pathlib.Path(input_path).glob("*_*_*_*.md")
    )
    logger.info(f"{len(document_files)} documents found.")
    document_files.sort(
        key=lambda doc: datetime.strptime(
            " ".join(str(doc.stem).split("_")[1:]), "%m %d %Y"
        )
    )
    document_files.reverse()
    return document_files


def group_documents_by_year(document_files: List[pathlib.Path]):
    years = {}

    logger.info("Grouping documents...")
    for file_ in document_files:
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
            str(output_path),
        ]
    )


def build_page(base: str, title: str, content: str, output_path: pathlib.Path):
    html = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="utf-8">
        <base href="{base}">
        <title>MUNCS Executive Docs. | {title}</title>
        <meta name="author" content="MUN Computer Science Society">
        <link rel="stylesheet" href="https://latex.now.sh/style.css">
    </head>

    <body>
        <header>
            <h1>MUNCS Executive Documents</h1>
            <p class="author">
            Last built {TODAY}
            </p>
            <a href=".."><p>Back a directory</p></a>
        </header>
        {content}
    </body>
    </html>
    """

    with open(output_path, "w") as f:
        f.write(html)


def build_docs(
    base: str, input_path_string: pathlib.Path, output_path_string: pathlib.Path
):
    input_path = pathlib.Path(input_path_string)
    output_path = pathlib.Path(output_path_string)

    json_output = []

    for doc_type in ["Agendas", "Minutes"]:
        doc_path = output_path / doc_type
        logger.info(f"Building '{doc_type}' documents")

        document_files = find_documents(input_path / doc_type)
        input_years = group_documents_by_year(document_files)

        doc_html_path = pathlib.Path(*doc_path.parts[1:])
        doc_html_header = f"""
        <a href="{doc_html_path}"><h2>Meeting {doc_type}</h2></a>
        """
        html_for_doc_type = str(doc_html_header)

        for year, months in input_years.items():
            year_path = doc_path / year
            logger.info(
                f"Building '{doc_type}' documents for {year} (output path {year_path})"
            )

            year_html_path = pathlib.Path(*year_path.parts[1:])
            year_html_header = f"""
            <a href="{year_html_path}"><h3>{year}</h3></a>
            """
            html_for_year = str(year_html_header)

            for month, files in months.items():
                month_path = year_path / month
                logger.info(
                    f"Building '{doc_type}' documents for {month} {year} (output path {month_path})"
                )
                month_path.mkdir(parents=True, exist_ok=True)

                month_html_path = pathlib.Path(*month_path.parts[1:])
                month_html_header = f"""
                <a href="{month_html_path}"><h4>{month}</h4></a>
                <ul>
                """
                html_for_month = str(month_html_header)

                for file_path in files:
                    file_output_name = file_path.stem + ".pdf"
                    file_output_path = month_path / file_output_name

                    run_pandoc_on_document(file_path, file_output_path)

                    file_time = key = datetime.strptime(
                        " ".join(str(file_output_path.stem).split("_")[1:]), "%m %d %Y"
                    )

                    html_path = pathlib.Path(*file_output_path.parts[1:])
                    html_for_month += f'<a href="{html_path}"><li>{file_time.strftime("%A, %B %e")}</li></a>\n'

                    json_output.append(
                        {"type": doc_type, "time": file_time, "path": html_path}
                    )

                html_for_month += "</ul>\n"
                html_for_year += html_for_month

                page = doc_html_header + year_html_header + html_for_month
                build_page(
                    base, f"{doc_type}, {month} {year}", page, month_path / "index.html"
                )

            html_for_doc_type += html_for_year

            page = doc_html_header + html_for_year
            build_page(base, f"{doc_type}, {year}", page, year_path / "index.html")

        build_page(
            base, f"{doc_type}, {year}", html_for_doc_type, doc_path / "index.html"
        )

    html_for_root = """
    <a href="./Minutes/"><h2>Meeting Minutes</h2></a>
    <a href="./Agendas/"><h2>Meeting Agendas</h2></a>
    """

    build_page(base, f"Index", html_for_root, output_path / "index.html")

    with open(output_path / "docs.json", "w") as f:
        json.dump(json_output, f, indent=4, sort_keys=True, default=str)


@click.group()
def cli():
    pass


@cli.command()
@click.option("-b", "--base", type=str, required=True)
@click.option(
    "-i", "--input", "input_path_string", type=click.Path(exists=True), required=True
)
@click.option(
    "-o", "--output", "output_path_string", type=click.Path(exists=True), required=True
)
def builddocs(base: str, input_path_string: str, output_path_string: str):
    input_path = pathlib.Path(input_path_string)
    output_path = pathlib.Path(output_path_string)

    build_docs(base, input_path, output_path)


if __name__ == "__main__":
    cli()
