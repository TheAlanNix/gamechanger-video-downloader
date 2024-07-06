FROM python:3.12-slim

RUN groupadd --gid 5000 user && useradd --home-dir /home/user --create-home --uid 5000 --gid 5000 --shell /bin/sh --skel /dev/null user
USER user

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /app

RUN mkdir videos

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY gamechanger/*.py gamechanger/
COPY downloader.py ./

ENTRYPOINT [ "python", "-u", "/app/downloader.py" ]