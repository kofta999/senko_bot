FROM python:3.8-slim-buster

WORKDIR /senko_bot
COPY help.json /senko_bot/help.json
COPY main.py /senko_bot/main.py
COPY cogs /senko_bot/cogs
COPY README.md /senko_bot/README.md
COPY .env /senko_bot/.env
COPY requirements.txt /senko_bot/requirements.txt
RUN pip install -r /senko_bot/requirements.txt
RUN pip install dpytools==0.18.0b0 --no-dependencies
CMD python3 main.py
