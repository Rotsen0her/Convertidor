# Script de Deploy SIN Docker (usando PM2)
# PowerShell

param(
    [string]$VPS_IP = "89.116.51.172",
    [string]$VPS_USER = "root",
    [string]$APP_DIR = "/var/www/convertidor",
    [switch]$SkipBuild,
    [switch]$SkipBackup,
    [switch]$SkipRestart
)

Write-Host "🚀 Deploy a $VPS_USER@$VPS_IP (modo PM2)" -ForegroundColor Cyan
Write-Host ""

# 1. Validar .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: No existe archivo .env" -ForegroundColor Red
    exit 1
}

# 2. Compilar CSS
if (-not $SkipBuild) {
    Write-Host "🎨 Compilando Tailwind CSS..." -ForegroundColor Cyan
    npm run build-css
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error compilando CSS" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ CSS compilado" -ForegroundColor Green
}

# 3. Backup (opcional)
if (-not $SkipBackup) {
    Write-Host "💾 Creando backup..." -ForegroundColor Cyan
    ssh "$VPS_USER@$VPS_IP" @"
        if [ -d $APP_DIR ]; then
            timestamp=`$(date +%Y%m%d_%H%M%S)
            tar -czf /tmp/convertidor_backup_`$timestamp.tar.gz $APP_DIR 2>/dev/null || true
            echo 'Backup: /tmp/convertidor_backup_'`$timestamp'.tar.gz'
        fi
"@
}

# 4. Sincronizar archivos desde backend/ hacia el servidor
Write-Host "📤 Sincronizando archivos..." -ForegroundColor Cyan

$currentPath = Get-Location
$wslPath = wsl wslpath -a "$currentPath"

# Sincronizar solo el contenido de backend/
wsl rsync -avz --progress `
    --exclude '__pycache__' `
    --exclude '*.pyc' `
    --exclude '*.log' `
    --exclude 'venv' `
    "$wslPath/backend/" "$VPS_USER@${VPS_IP}:${APP_DIR}/"

# Sincronizar ecosystem.config.js si existe en la raíz
if (Test-Path "ecosystem.config.js") {
    wsl rsync -avz --progress `
        "$wslPath/ecosystem.config.js" "$VPS_USER@${VPS_IP}:${APP_DIR}/"
}

# Sincronizar start_gunicorn.sh adaptado para PM2
wsl rsync -avz --progress `
    "$wslPath/backend/start_gunicorn.sh" "$VPS_USER@${VPS_IP}:${APP_DIR}/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error sincronizando" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Archivos sincronizados" -ForegroundColor Green

# 5. Instalar dependencias y configurar
Write-Host "⚙️  Configurando en servidor..." -ForegroundColor Cyan

ssh "$VPS_USER@$VPS_IP" @"
    set -e
    cd $APP_DIR
    
    # Verificar virtualenv
    if [ ! -d venv ]; then
        echo '📦 Creando virtualenv...'
        python3 -m venv venv
    fi
    
    # Activar virtualenv e instalar/actualizar dependencias
    echo '📦 Instalando dependencias...'
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Verificar .env
    if [ ! -f .env ]; then
        echo '⚠️  Archivo .env no existe en el servidor'
        echo 'Cópialo manualmente con: scp .env $VPS_USER@$VPS_IP:$APP_DIR/.env'
        exit 1
    fi
    
    # Verificar y corregir CRLF en .env
    sed -i 's/\r$//' .env
    
    # Dar permisos al script
    chmod +x start_gunicorn.sh
    
    # Crear directorio de cache
    mkdir -p /tmp/convertidor_cache
    chmod 755 /tmp/convertidor_cache
    
    echo '✅ Configuración completada'
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en configuración" -ForegroundColor Red
    exit 1
}

# 6. Reiniciar PM2 (opcional)
if (-not $SkipRestart) {
    Write-Host "🔄 Reiniciando PM2..." -ForegroundColor Cyan
    
    ssh "$VPS_USER@$VPS_IP" @"
        cd $APP_DIR
        
        # Verificar si PM2 está instalado
        if ! command -v pm2 &> /dev/null; then
            echo '❌ PM2 no está instalado'
            echo 'Instálalo con: npm install -g pm2'
            exit 1
        fi
        
        # Reiniciar o iniciar aplicación
        if pm2 list | grep -q convertidor-flask; then
            echo '🔄 Reiniciando aplicación...'
            pm2 reload convertidor-flask --update-env
        else
            echo '🚀 Iniciando aplicación por primera vez...'
            if [ -f ecosystem.config.js ]; then
                pm2 start ecosystem.config.js
            else
                pm2 start start_gunicorn.sh --name convertidor-flask --interpreter bash
            fi
        fi
        
        pm2 save
        
        echo ''
        echo '✅ Aplicación reiniciada'
        echo ''
        pm2 list
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Deploy exitoso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
        Write-Host "  Ver logs:    ssh $VPS_USER@$VPS_IP 'pm2 logs convertidor-flask'"
        Write-Host "  Reiniciar:   ssh $VPS_USER@$VPS_IP 'pm2 restart convertidor-flask'"
        Write-Host "  Ver estado:  ssh $VPS_USER@$VPS_IP 'pm2 list'"
        Write-Host "  Monitorear:  ssh $VPS_USER@$VPS_IP 'pm2 monit'"
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Error reiniciando PM2" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "✅ Archivos sincronizados (sin reiniciar)" -ForegroundColor Green
    Write-Host "Para reiniciar: ssh $VPS_USER@$VPS_IP 'pm2 reload convertidor-flask'" -ForegroundColor Yellow
}
