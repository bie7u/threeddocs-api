FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["gunicorn", "threeddocs.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
