FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bridges/ ./bridges/
COPY configs/ ./configs/
COPY schemas/ ./schemas/
COPY scripts/ ./scripts/

RUN mkdir -p /var/lib/bridge/queue

RUN useradd -m -u 1000 bridge && chown -R bridge:bridge /app /var/lib/bridge
USER bridge

EXPOSE 8090 9090

CMD ["python", "-m", "bridges.core"]
