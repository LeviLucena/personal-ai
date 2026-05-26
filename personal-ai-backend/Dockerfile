FROM python:3.12-slim

WORKDIR /app

# Install build dependencies for psycopg/asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy everything so setuptools can find src/
COPY pyproject.toml .
COPY src/ src/

# Install project
RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
