#!/bin/bash
# Script de deploy COMPLETO para primera instalación o reinstalación total
set -e

echo "🚀 DEPLOY COMPLETO - Primera instalación"
echo "⚠️  Este script reconstruirá TODO desde cero"
echo ""
read -p "¿Continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Deploy cancelado"
    exit 1
fi

echo ""
echo "📥 Clonando/Actualizando repositorio..."
git pull origin main || git clone https://github.com/Rotsen0her/Convertidor.git .

echo ""
echo "📦 Instalando dependencias de Node..."
npm install

echo ""
echo "🎨 Compilando Tailwind CSS..."
npm run build-css

echo ""
echo "📁 Creando estructura de directorios..."
mkdir -p backend/static/css
mkdir -p backend/static/js
mkdir -p backend/static/images
mkdir -p backend/uploads
mkdir -p backend/transformados
mkdir -p nginx/certbot/conf
mkdir -p nginx/certbot/www

echo ""
echo "🔐 Verificando archivo .env..."
if [ ! -f ".env" ]; then
    echo "⚠️  Creando .env desde .env.example..."
    cp .env.example .env
    echo "❗ IMPORTANTE: Edita el archivo .env con tus valores reales"
    echo "   nano .env"
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

echo ""
echo "🔧 Configurando permisos..."
chmod +x backend/start_gunicorn.sh
chmod +x deploy.sh
chmod +x reset-admin.sh

echo ""
echo "🐳 Construyendo y levantando contenedores..."
docker compose down -v  # Elimina volúmenes también (¡CUIDADO!)
docker compose up -d --build

echo ""
echo "⏳ Esperando a que MySQL esté listo..."
sleep 15

echo ""
echo "📊 Estado de contenedores:"
docker compose ps

echo ""
echo "✅ Deploy completo finalizado!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Configurar dominio para apuntar a este servidor"
echo "   2. Configurar SSL con: docker compose exec nginx certbot --nginx -d tu-dominio.com"
echo "   3. Acceder a: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "🔍 Ver logs:"
echo "   docker compose logs -f"
