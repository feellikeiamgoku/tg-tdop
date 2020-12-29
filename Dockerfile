FROM python:3.9-slim

RUN mkdir bot

WORKDIR bot

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .


ENTRYPOINT python main.py
