# Script de Deploy Rápido para Docker
# PowerShell

param(
    [string]$VPS_IP = "89.116.51.172",
    [string]$VPS_USER = "root",
    [string]$DEPLOY_PATH = "/var/www/Convertidor",
    [switch]$SkipBuild
)

Write-Host "🚀 Deploy Docker a luziia.cloud" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Validar .env
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: No existe .env localmente" -ForegroundColor Yellow
    Write-Host "Asegúrate de configurarlo en el servidor" -ForegroundColor Yellow
}

# 2. Compilar Tailwind CSS
if (-not $SkipBuild) {
    Write-Host "🎨 Compilando Tailwind CSS..." -ForegroundColor Cyan
    npm run build-css
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error compilando CSS" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ CSS compilado" -ForegroundColor Green
} else {
    Write-Host "⏭️  Saltando compilación de CSS" -ForegroundColor Yellow
}

# 3. Verificar que output.css existe
if (-not (Test-Path "backend/static/css/output.css")) {
    Write-Host "❌ Error: backend/static/css/output.css no existe" -ForegroundColor Red
    Write-Host "Ejecuta: npm run build-css" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📤 Sincronizando archivos..." -ForegroundColor Cyan

# 4. Sincronizar archivos
$currentPath = Get-Location
$wslPath = wsl wslpath -a "$currentPath"

wsl rsync -avz --progress --delete `
    --exclude 'node_modules' `
    --exclude '.git' `
    --exclude '.env' `
    --exclude '*.pyc' `
    --exclude '__pycache__' `
    --exclude 'venv' `
    --exclude '*.log' `
    "$wslPath/" "$VPS_USER@${VPS_IP}:${DEPLOY_PATH}/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error sincronizando archivos" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Archivos sincronizados" -ForegroundColor Green

# 5. Deploy con Docker Compose
Write-Host ""
Write-Host "🐳 Desplegando con Docker Compose..." -ForegroundColor Cyan

ssh "$VPS_USER@$VPS_IP" @"
    set -e
    cd $DEPLOY_PATH
    
    # Verificar .env
    if [ ! -f .env ]; then
        echo '❌ Error: .env no existe en el servidor'
        echo 'Crea el archivo .env antes de continuar'
        exit 1
    fi
    
    # Detener contenedores actuales
    echo '🛑 Deteniendo contenedores...'
    docker-compose down
    
    # Construir imágenes
    echo '🏗️  Construyendo imágenes...'
    docker-compose build --no-cache
    
    # Iniciar servicios
    echo '🚀 Iniciando servicios...'
    docker-compose up -d
    
    # Esperar a que inicien
    echo '⏳ Esperando a que los servicios inicien...'
    sleep 10
    
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
    Write-Host "📋 URLs:" -ForegroundColor Cyan
    Write-Host "  HTTP:  http://luziia.cloud" -ForegroundColor White
    Write-Host "  HTTPS: https://luziia.cloud (configurar Certbot)" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
    Write-Host "  Ver logs:      ssh $VPS_USER@$VPS_IP 'cd $DEPLOY_PATH && docker-compose logs -f'"
    Write-Host "  Ver estado:    ssh $VPS_USER@$VPS_IP 'cd $DEPLOY_PATH && docker-compose ps'"
    Write-Host "  Reiniciar:     ssh $VPS_USER@$VPS_IP 'cd $DEPLOY_PATH && docker-compose restart'"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Error en el deploy" -ForegroundColor Red
    Write-Host "Ver logs: ssh $VPS_USER@$VPS_IP 'cd $DEPLOY_PATH && docker-compose logs'" -ForegroundColor Yellow
    exit 1
}
