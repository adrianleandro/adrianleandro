FROM python:3.11.0-alpine
RUN apk add docker
RUN pip install --no-cache-dir pyyaml
WORKDIR /app

COPY ./cmd/health/main.py .
COPY ../configs/health_checker_config.ini ./
COPY ../compose.yml ./
COPY ./internal/health ./src

ENTRYPOINT ["python3", "main.py"]