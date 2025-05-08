# 1. Basis-Image
FROM python:3.12-slim

# 2. (Optional) System-Tools, falls du C-Builds brauchst
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# 3. Abhängigkeiten separat, damit Docker-Cache greift
WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Quellcode: **nur den Inhalt von dash_app/**
WORKDIR /dash_app
COPY dash_app/ .

# 5. Port 80 nach außen
EXPOSE 80

# 6. Start-Command
CMD ["gunicorn", "app:server",              \
     "--workers", "4", "--threads", "2",    \
     "--bind", "0.0.0.0:80", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
