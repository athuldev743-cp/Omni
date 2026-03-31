FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy ONLY requirements first — pip layer only rebuilds when
#    requirements.txt actually changes, not on every code change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy code last — cache miss here doesn't re-run pip
COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]