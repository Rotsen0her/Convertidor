#!/bin/bash
# Script de inicio para Gunicorn en Docker
set -e

# Directorio de trabajo dentro del contenedor
APP_DIR="/app"
cd "$APP_DIR"

# Las variables de entorno ya están cargadas por docker-compose (env_file)
# Así que no necesitamos source .env aquí

# Ejecutar gunicorn
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 app:app
