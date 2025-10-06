#!/bin/bash
# Script de actualización rápida para aplicación desplegada
set -e  # Salir si hay error

echo "🚀 Actualizando Convertidor..."

# Backup de archivos críticos antes del pull
echo "💾 Backup de configuración..."
[ -f "nginx/default.conf" ] && cp nginx/default.conf nginx/default.conf.backup
[ -f ".env" ] && cp .env .env.backup

# Actualizar código desde GitHub
echo "📥 Obteniendo cambios desde GitHub..."

# Verificar si hay conflictos pendientes
if git diff --name-only --diff-filter=U | grep -q .; then
    echo "⚠️  Hay conflictos sin resolver. Limpiando..."
    git reset --hard
fi

# Guardar cambios locales temporalmente
git stash

# Pull desde GitHub
if ! git pull origin main; then
    echo "❌ Error al hacer pull. Revirtiendo..."
    git stash pop 2>/dev/null || true
    exit 1
fi

# Restaurar cambios locales si existen
git stash pop 2>/dev/null || echo "✓ Sin cambios locales"

# Instalar/actualizar dependencias si package.json cambió
if git diff HEAD@{1} --name-only | grep -q "package.json"; then
    echo "📦 Actualizando dependencias npm..."
    npm install
fi

# Compilar Tailwind CSS solo si hay cambios en frontend
if git diff HEAD@{1} --name-only | grep -qE "(tailwind|\.css|templates/)"; then
    echo "🎨 Compilando Tailwind CSS..."
    npm run build-css
else
    echo "⏭️  CSS sin cambios"
fi

# Reiniciar solo contenedores necesarios (sin rebuild completo)
echo "🔄 Reiniciando servicios..."

# Detectar qué cambió para reiniciar solo lo necesario
BACKEND_CHANGED=$(git diff HEAD@{1} --name-only | grep -E "^backend/" || true)
NGINX_CHANGED=$(git diff HEAD@{1} --name-only | grep -E "^nginx/" || true)

if [ -n "$BACKEND_CHANGED" ]; then
    echo "   ↻ Backend modificado, reiniciando..."
    docker compose restart backend
else
    echo "   ✓ Backend sin cambios"
fi

if [ -n "$NGINX_CHANGED" ]; then
    echo "   ↻ Nginx modificado, reiniciando..."
    
    # Restaurar SSL si se sobrescribió
    if [ -f "nginx/default.conf.backup" ]; then
        if ! grep -q "ssl_certificate" nginx/default.conf; then
            echo "   ⚠️  Restaurando config SSL..."
            mv nginx/default.conf.backup nginx/default.conf
        fi
    fi
    
    docker compose restart nginx
else
    echo "   ✓ Nginx sin cambios"
fi

# Limpiar backups si todo está bien
[ -f "nginx/default.conf.backup" ] && rm -f nginx/default.conf.backup
[ -f ".env.backup" ] && rm -f .env.backup

echo ""
echo "✅ Actualización completada!"
echo "📊 Estado de servicios:"
docker compose ps

echo ""
echo "🌐 Aplicación: https://luziia.cloud"
echo "🔍 Ver logs: docker compose logs -f backend"