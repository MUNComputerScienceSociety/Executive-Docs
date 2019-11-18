FROM pandoc/latex:2.6

ADD entrypoint.py /entrypoint.py
RUN apk add python3
ENTRYPOINT [ "python3", "/entrypoint.py" ]