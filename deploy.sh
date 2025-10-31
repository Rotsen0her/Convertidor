#!/bin/bash
# Script de actualización para múltiples servicios Docker
set -e  # Salir si hay error

echo "🚀 Actualizando TODOS los servicios..."

# --- 1. Definir directorios de servicios ---
# Añade más carpetas aquí en el futuro.
# Se desplegarán en este orden.
SERVICE_DIRS=(
    "nginx-proxy"  # El proxy primero
    "wordpress"    # Luego WordPress
    "."            # La aplicación principal (de última)
)

# --- 2. Backup de archivos críticos ---
echo "💾 Backup de configuración..."
# Solo hacemos backup del .env de la app principal
[ -f ".env" ] && cp .env .env.backup

# --- 3. Actualizar código desde GitHub ---
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

# Guardar .env de la app principal
git stash push -m "deploy-backup" .env 2>/dev/null || echo "✓ Sin .env local que guardar"

# Pull desde GitHub
echo "⬇️  Descargando cambios..."
if ! git pull origin main; then
    echo "❌ Error al hacer pull"
    git stash pop 2>/dev/null || true
    exit 1
fi

# Restaurar .env
if git stash list | grep -q "deploy-backup"; then
    git stash pop 2>/dev/null || echo "✓ .env local restaurado"
fi

# --- 4. Build de Frontend (si es necesario) ---
# Esto se ejecuta en el directorio raíz ('.')
if git diff HEAD@{1} --name-only | grep -q "package.json"; then
    echo "📦 Actualizando dependencias npm..."
    npm install
fi

if git diff HEAD@{1} --name-only | grep -qE "(tailwind|\.css|templates/|package\.json)"; then
    echo "🎨 Compilando Tailwind CSS..."
    npm run build-css
else
    echo "⏭️  CSS sin cambios"
fi

# --- 5. Reiniciar TODOS los servicios Docker ---
echo "🔄 Reiniciando servicios Docker en orden..."

for dir in "${SERVICE_DIRS[@]}"; do
    echo "--- Actualizando servicios en: $dir ---"
    ( # Usar un subshell para no cambiar el directorio actual del script
        cd "$dir"
        
        if [ "$dir" = "." ]; then
            # App principal: reconstruir el backend si es necesario
            echo "   (Reconstruyendo app principal...)"
            docker compose up -d --build --remove-orphans
        else
            # Otros servicios (como NPM): solo 'up' (pull de imagen nueva)
            echo "   (Actualizando servicio...)"
            docker compose up -d --remove-orphans
        fi
    )
done

# --- 6. Limpieza ---
[ -f ".env.backup" ] && rm -f .env.backup

echo ""
echo "✅ Actualización completada!"
echo "📊 Estado de servicios (de la app principal):"
docker compose ps  # Esto solo mostrará los servicios del compose en '.'

echo ""
echo "🌐 Aplicación: https://luziia.cloud"
echo "🔍 Ver logs (backend): docker compose logs -f backend"
echo "🔍 Ver logs (proxy): docker compose -f nginx-proxy/docker-compose.yml logs -f"
