# MUN Computer Science Society Executive Docs

This repository contains executive documents for the society that are intended for public access, such as meeting agendas and minutes.

The compiled version of all of the documents in PDF format [can be found here.](https://www.cs.mun.ca/~csclub/executive-documents/)

Once updates are pushed to `master`, the website is updated automatically.

## Format

Agendas and meeting minutes will be written with Markdown, and compiled to a final PDF for easier reading, printing, and sharing using Pandoc.

For details on the Markdown formatting used, refer to the [Pandoc Markdown manual.](https://pandoc.org/MANUAL.html)

## Creating an agenda/meeting minute

To create an agenda or meeting minute, copy the respective `<TYPE>_TEMPLATE.md` file to `<TYPE>_<MM>_<DD>_<YYYY>.md`, and fill out the data it asks for.

## Development

### Docker

* From the root of the repository, build the base image:

```bash
docker build . -t executive-docs
```

* Build the documents:

```bash
docker run -it --rm -v "$(pwd):/tmp" -w /tmp executive-docs /bin/bash -c "mkdir -p ./executive-documents/; python3 cli.py builddocs --base /~csclub/executive-documents/ --input . --output ./executive-documents/"
```

* The new documents will be generated in your ./executive-documents directory.

