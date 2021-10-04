FROM python:3.9

RUN apt update && apt -y install ffmpeg

WORKDIR /usr/src/app

COPY ./src ./src
COPY ./setup.cfg .
COPY ./setup.py .
COPY ./pyproject.toml .

RUN pip install --no-cache-dir -e .

CMD [ "dipthid", "watch", "/usr/src/app/watch"]