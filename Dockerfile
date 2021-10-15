FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libmariadb-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim

COPY --from=builder /opt/venv /opt/venv

RUN apt-get update && apt-get -y --no-install-recommends install ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN addgroup --system app && adduser --home /app --system --group app
RUN chown -R app:app /opt/venv

USER app

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

COPY ./setup.cfg .
COPY ./setup.py .
COPY ./pyproject.toml .

COPY ./src ./src

RUN pip install --no-cache-dir .

ENTRYPOINT [ "dipthid", "watch", "/app/watch"]

CMD ["--post-processer=dipthid.postprocessing:PostProcessLog"]

HEALTHCHECK CMD ps -ef | grep "[d]ipthid" || exit 1