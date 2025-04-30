# 1. Basis-Image: Python 3.12 slim
FROM python:3.12-slim

# 2. Arbeitsverzeichnis
WORKDIR /dash_app

# 3. System-Abhängigkeiten (falls du build-tools o. ä. brauchst)
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# 4. Copy requirements und install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy des gesamten Projekts
COPY . .

# 6. Expose Port (Dash-Default)
EXPOSE 80

# 7. Start mit Gunicorn
CMD ["gunicorn", "app:server", \
     "--workers", "4", \
     "--threads", "2", \
     "--bind", "0.0.0.0:80", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
