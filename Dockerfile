FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
WORKDIR /app/src
RUN chmod +x /app/src/start.sh

EXPOSE 8000

CMD ["/app/src/start.sh"]
