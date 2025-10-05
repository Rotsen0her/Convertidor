#!/bin/bash
# Script de inicio para Gunicorn en Docker
set -e

# Directorio de trabajo dentro del contenedor
APP_DIR="/app"
cd "$APP_DIR"

# Las variables de entorno ya están cargadas por docker-compose (env_file)
# Así que no necesitamos source .env aquí

# Ejecutar gunicorn
exec gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 --log-level info app:app
