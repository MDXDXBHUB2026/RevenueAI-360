FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY domain ./domain
COPY shared ./shared
COPY services ./services
COPY tools ./tools
COPY agents ./agents
COPY connectors ./connectors
COPY apps/api ./apps/api

# Install dependencies and local package
RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    LLM_PROVIDER=deterministic_demo

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
