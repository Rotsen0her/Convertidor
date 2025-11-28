#!/bin/bash
# Script de inicio para Gunicorn en Docker
set -e

# Directorio de trabajo dentro del contenedor
APP_DIR="/app"
cd "$APP_DIR"

# Las variables de entorno ya están cargadas por docker-compose (env_file)
# Así que no necesitamos source .env aquí

# Ejecutar gunicorn con configuración para archivos grandes
# - workers: 4 (aumentado para mejor paralelización)
# - timeout: 3600 (1 hora para archivos muy grandes)
# - worker-tmp-dir: usar /dev/shm (memoria compartida) para mejor rendimiento
# - max-requests: reiniciar workers cada 100 requests para liberar memoria
exec gunicorn --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class gevent \
  --timeout 3600 \
  --graceful-timeout 3600 \
  --keep-alive 5 \
  --max-requests 100 \
  --max-requests-jitter 10 \
  --worker-tmp-dir /dev/shm \
  app:app
