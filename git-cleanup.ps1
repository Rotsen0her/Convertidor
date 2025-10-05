# Script para limpiar archivos sensibles del historial de Git
# ⚠️ IMPORTANTE: Este script modificará el historial de Git
# Ejecutar ANTES de hacer push si tienes archivos sensibles en el historial

Write-Host "🧹 Limpieza de repositorio Git" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$currentLocation = Get-Location

# Verificar que estamos en un repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "❌ Error: No estás en un repositorio Git" -ForegroundColor Red
    exit 1
}

Write-Host "⚠️  ADVERTENCIA:" -ForegroundColor Yellow
Write-Host "Este script eliminará archivos sensibles del historial de Git." -ForegroundColor Yellow
Write-Host "Esto puede causar conflictos si ya hiciste push a GitHub." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "¿Continuar? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "📋 Paso 1: Eliminar archivos del índice de Git" -ForegroundColor Cyan

# Archivos sensibles que deben eliminarse del tracking
$filesToRemove = @(
    ".env",
    "__pycache__/",
    "scripts/__pycache__/",
    "*.pyc",
    "static/css/output.css"
)

foreach ($file in $filesToRemove) {
    Write-Host "  Removiendo: $file" -ForegroundColor Gray
    git rm -r --cached $file 2>$null
}

Write-Host "✅ Archivos removidos del índice" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Paso 2: Verificar estado actual" -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "📋 Paso 3: Crear commit de limpieza" -ForegroundColor Cyan
git add .gitignore

$commitMessage = "🔒 Actualizar .gitignore y remover archivos sensibles

- Mejorado .gitignore con más patrones
- Removido .env del tracking (SEGURIDAD)
- Removido __pycache__ del tracking
- Removido output.css generado
- Agregadas exclusiones para Docker, backups, etc.
"

git commit -m $commitMessage

Write-Host "✅ Commit creado" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Paso 4: Eliminar del historial (OPCIONAL)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si quieres eliminar estos archivos del HISTORIAL completo:" -ForegroundColor Yellow
Write-Host ""
Write-Host "git filter-branch --force --index-filter \\" -ForegroundColor Gray
Write-Host "  'git rm --cached --ignore-unmatch .env __pycache__/*.pyc' \\" -ForegroundColor Gray
Write-Host "  --prune-empty --tag-name-filter cat -- --all" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  SOLO ejecuta esto si NO has hecho push todavía" -ForegroundColor Yellow
Write-Host ""

$cleanHistory = Read-Host "¿Limpiar historial completo? (yes/no)"

if ($cleanHistory -eq "yes") {
    Write-Host ""
    Write-Host "🧹 Limpiando historial..." -ForegroundColor Cyan
    
    git filter-branch --force --index-filter `
        "git rm --cached --ignore-unmatch .env __pycache__/*.pyc scripts/__pycache__/*.pyc static/css/output.css" `
        --prune-empty --tag-name-filter cat -- --all
    
    Write-Host "✅ Historial limpiado" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Para completar la limpieza:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "git reflog expire --expire=now --all" -ForegroundColor Gray
    Write-Host "git gc --prune=now --aggressive" -ForegroundColor Gray
    Write-Host ""
    
    $gcNow = Read-Host "¿Ejecutar limpieza profunda ahora? (yes/no)"
    if ($gcNow -eq "yes") {
        git reflog expire --expire=now --all
        git gc --prune=now --aggressive
        Write-Host "✅ Limpieza profunda completada" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ ¡Limpieza completada!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Verifica que .env NO esté en 'git status'" -ForegroundColor White
Write-Host "2. Si ya hiciste push antes, usa: git push --force origin main" -ForegroundColor White
Write-Host "3. Si es la primera vez, usa: git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Recuerda:" -ForegroundColor Yellow
Write-Host "- NUNCA subas el archivo .env a GitHub" -ForegroundColor Yellow
Write-Host "- Usa .env.example para documentar variables necesarias" -ForegroundColor Yellow
Write-Host "- Configura .env manualmente en cada servidor" -ForegroundColor Yellow
Write-Host ""
