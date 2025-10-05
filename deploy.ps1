# Script de Deploy para VPS usando Docker
# PowerShell

param(
    [string]$VPS_IP = "89.116.51.172",
    [string]$VPS_USER = "root",
    [switch]$SkipBuild,
    [switch]$SkipBackup
)

Write-Host "🚀 Iniciando deploy a $VPS_USER@$VPS_IP" -ForegroundColor Cyan
Write-Host ""

# 1. Validar que existe .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: No existe archivo .env" -ForegroundColor Red
    Write-Host "Copia .env.example a .env y configura las variables" -ForegroundColor Yellow
    exit 1
}

# 2. Compilar Tailwind CSS localmente
if (-not $SkipBuild) {
    Write-Host "🎨 Compilando Tailwind CSS..." -ForegroundColor Cyan
    npm run build-css
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error compilando CSS" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ CSS compilado" -ForegroundColor Green
}

# 3. Crear backup en servidor (opcional)
if (-not $SkipBackup) {
    Write-Host "💾 Creando backup en servidor..." -ForegroundColor Cyan
    ssh "$VPS_USER@$VPS_IP" @"
        if [ -d /var/www/convertidor ]; then
            timestamp=`$(date +%Y%m%d_%H%M%S)
            tar -czf /tmp/convertidor_backup_`$timestamp.tar.gz /var/www/convertidor 2>/dev/null || true
            echo 'Backup creado: /tmp/convertidor_backup_'`$timestamp'.tar.gz'
        fi
"@
}

# 4. Sincronizar archivos al servidor (usando WSL rsync)
Write-Host "📤 Sincronizando archivos al servidor..." -ForegroundColor Cyan

# Convertir ruta Windows a WSL
$currentPath = Get-Location
$wslPath = wsl wslpath -a "$currentPath"

wsl rsync -avz --progress --delete `
    --exclude 'node_modules' `
    --exclude 'venv' `
    --exclude '__pycache__' `
    --exclude '.git' `
    --exclude '.env' `
    --exclude '*.pyc' `
    --exclude '*.log' `
    --exclude 'uploads' `
    --exclude 'transformados' `
    "$wslPath/" "$VPS_USER@${VPS_IP}:/var/www/convertidor/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error sincronizando archivos" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Archivos sincronizados" -ForegroundColor Green

# 5. Configurar y ejecutar en el servidor
Write-Host "⚙️  Configurando servidor..." -ForegroundColor Cyan

ssh "$VPS_USER@$VPS_IP" @"
    set -e
    cd /var/www/convertidor
    
    # Verificar que existe docker-compose
    if ! command -v docker-compose &> /dev/null; then
        echo '❌ docker-compose no está instalado'
        exit 1
    fi
    
    # Copiar .env si no existe
    if [ ! -f .env ]; then
        echo '⚠️  No existe .env en el servidor, debes crearlo manualmente'
        exit 1
    fi
    
    # Detener contenedores actuales
    echo '🛑 Deteniendo contenedores...'
    docker-compose down
    
    # Construir imágenes
    echo '🏗️  Construyendo imágenes...'
    docker-compose build
    
    # Iniciar servicios
    echo '🚀 Iniciando servicios...'
    docker-compose up -d
    
    # Esperar a que MySQL esté listo
    echo '⏳ Esperando a que MySQL esté listo...'
    sleep 10
    
    # Importar base de datos si existe init-db.sql
    if [ -f init-db.sql ]; then
        echo '📊 Inicializando base de datos...'
        docker-compose exec -T db mysql -u root -p\$MYSQL_ROOT_PASSWORD < init-db.sql || true
    fi
    
    # Mostrar estado
    echo ''
    echo '✅ Deploy completado!'
    echo ''
    docker-compose ps
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Deploy exitoso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
    Write-Host "  Ver logs:      ssh $VPS_USER@$VPS_IP 'cd /var/www/convertidor && docker-compose logs -f'"
    Write-Host "  Reiniciar:     ssh $VPS_USER@$VPS_IP 'cd /var/www/convertidor && docker-compose restart'"
    Write-Host "  Ver estado:    ssh $VPS_USER@$VPS_IP 'cd /var/www/convertidor && docker-compose ps'"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Error en el deploy" -ForegroundColor Red
    exit 1
}
