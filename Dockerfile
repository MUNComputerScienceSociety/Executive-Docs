FROM ubuntu:latest

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive TZ=America/St_Johns apt-get install -y pandoc texlive-full texlive-fonts-recommended python3-pip
RUN pip install --upgrade pip

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt
