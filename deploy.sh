#!/bin/bash
# Script de deploy automatizado

echo "🚀 Iniciando deploy de Convertidor..."

# Actualizar código
git pull origin main

# Compilar Tailwind CSS
echo "🎨 Compilando Tailwind CSS..."
npm run build:css

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p nginx/certbot/conf
mkdir -p nginx/certbot/www

# Dar permisos al script de gunicorn
chmod +x backend/start_gunicorn.sh

# Reconstruir y levantar contenedores
echo "🐳 Reconstruyendo contenedores..."
docker compose down
docker compose up -d --build

echo "✅ Deploy completado!"
echo "📊 Estado de los contenedores:"
docker-compose ps
