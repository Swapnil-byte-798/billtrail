FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/data
WORKDIR /app
COPY pyproject.toml ./
COPY billtrail ./billtrail
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir . && useradd -m -u 10001 app && mkdir /data && chown app:app /data
USER app
CMD ["python", "-m", "uvicorn", "billtrail.api:app", "--host", "0.0.0.0", "--port", "8020"]
