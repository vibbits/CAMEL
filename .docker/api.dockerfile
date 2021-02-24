FROM python:3.8-buster

RUN apt update && apt -y dist-upgrade
RUN apt install -y default-libmysqlclient-dev build-essential --no-install-recommends

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r ./requirements.txt
ENV APP_PATH="/app"

ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "Camel:app"]
