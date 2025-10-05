# Script para compilar Tailwind CSS en PowerShell

Write-Host "📦 Instalando dependencias..." -ForegroundColor Cyan
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
    Write-Host "`n🎨 Compilando Tailwind CSS..." -ForegroundColor Cyan
    npm run build:css
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ CSS compilado exitosamente en backend/static/css/output.css" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al compilar CSS" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}
