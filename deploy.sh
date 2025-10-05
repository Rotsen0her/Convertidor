#!/bin/bash
# Script de deploy automatizado para VPS con Nginx externo

echo "🚀 Iniciando deploy de Convertidor..."

# Actualizar código
echo "📥 Actualizando código desde GitHub..."
git pull origin main

# Instalar dependencias de Node si es necesario
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias de Node..."
    npm install
fi

# Compilar Tailwind CSS
echo "🎨 Compilando Tailwind CSS..."
npm run build:css

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p backend/static/css
mkdir -p backend/static/js
mkdir -p backend/static/images
mkdir -p nginx/certbot/conf
mkdir -p nginx/certbot/www

# Dar permisos al script de gunicorn
chmod +x backend/start_gunicorn.sh

# Reconstruir y levantar contenedores
echo "🐳 Reconstruyendo contenedores..."
docker-compose down
docker-compose up -d --build

echo "✅ Deploy completado!"
echo "📊 Estado de los contenedores:"
docker-compose ps

echo ""
echo "🌐 Tu aplicación debería estar disponible en:"
echo "   http://convertidor.synapzys.com"
