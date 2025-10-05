#!/bin/bash
# Script de deploy automatizado para VPS con Nginx externo
set -e  # Salir si hay error

echo "🚀 Iniciando deploy de Convertidor..."

# Backup de archivos críticos antes del pull
echo "💾 Creando backup de configuración..."
if [ -f "nginx/default.conf" ]; then
    cp nginx/default.conf nginx/default.conf.backup
fi
if [ -f ".env" ]; then
    cp .env .env.backup
fi

# Actualizar código
echo "📥 Actualizando código desde GitHub..."
git stash  # Guardar cambios locales temporalmente
git pull origin main
git stash pop || echo "⚠️  No hay cambios locales que restaurar"

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
docker compose down
docker compose up -d --build

# Restaurar configuración SSL si hay conflictos
if [ -f "nginx/default.conf.backup" ]; then
    if ! grep -q "ssl_certificate" nginx/default.conf; then
        echo "⚠️  Configuración SSL no detectada, restaurando backup..."
        mv nginx/default.conf.backup nginx/default.conf
    else
        rm nginx/default.conf.backup
    fi
fi

echo "✅ Deploy completado!"
echo "📊 Estado de los contenedores:"
docker compose ps

echo ""
echo "🌐 Tu aplicación debería estar disponible en:"
echo "   https://luziia.cloud"
echo ""
echo "🔍 Verificar logs:"
echo "   docker compose logs -f backend"
