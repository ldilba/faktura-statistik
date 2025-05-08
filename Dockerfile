# 1. Basis-Image
FROM python:3.12-slim

# 2. Arbeitsverzeichnis ausserhalb des Pakets
WORKDIR /app

# 3. Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Nur das eigentliche Paket kopieren
COPY dash_app ./dash_app
# (optional) sicherstellen, dass dash_app als Paket gilt
# RUN touch dash_app/__init__.py

# 5. Expose Port 80
EXPOSE 80

# 6. Start-Befehl
CMD ["gunicorn", "dash_app.app:server", \
     "--workers", "4", "--threads", "2", \
     "--bind", "0.0.0.0:80", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
