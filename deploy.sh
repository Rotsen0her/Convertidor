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

# Verificar si hay un merge en curso y abortarlo
if [ -f ".git/MERGE_HEAD" ] || git status | grep -q "Unmerged paths"; then
    echo "⚠️  Abortando merge en curso..."
    git merge --abort 2>/dev/null || true
    git reset --hard origin/main
fi

# Descartar cambios en archivos que se generan automáticamente
echo "🧹 Limpiando archivos generados automáticamente..."
git checkout -- package-lock.json 2>/dev/null || true

# Guardar cambios locales solo de archivos críticos (.env y nginx)
git stash push -m "deploy-backup" .env nginx/default.conf 2>/dev/null || echo "✓ Sin cambios críticos locales"

# Pull desde GitHub
echo "⬇️  Descargando cambios..."
if ! git pull origin main; then
    echo "❌ Error al hacer pull"
    git stash pop 2>/dev/null || true
    exit 1
fi

# Restaurar configuración local si existe
if git stash list | grep -q "deploy-backup"; then
    git stash pop 2>/dev/null || echo "✓ Configuración local restaurada"
fi

# Instalar/actualizar dependencias si package.json cambió
if git diff HEAD@{1} --name-only | grep -q "package.json"; then
    echo "📦 Actualizando dependencias npm..."
    npm install
fi

# Compilar Tailwind CSS solo si hay cambios en frontend
if git diff HEAD@{1} --name-only | grep -qE "(tailwind|\.css|templates/|package\.json)"; then
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