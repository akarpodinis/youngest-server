FROM python:3.14-slim-bookworm

WORKDIR /app

COPY app/server.py .

EXPOSE 8000

CMD ["python", "server.py"]
