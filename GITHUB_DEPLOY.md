# 🚀 Deploy Automático con GitHub

Esta guía explica cómo configurar deploy automático a tu VPS usando GitHub Actions.

## 📋 Ventajas del Deploy con GitHub

✅ **Automático** - Push a `main` → Deploy instantáneo  
✅ **Historial** - Todos los deploys quedan registrados  
✅ **Rollback fácil** - Revertir a cualquier commit anterior  
✅ **CI/CD** - Compilación de CSS automática  
✅ **Sin contraseñas** - Usa SSH keys seguras  
✅ **Logs completos** - Ver qué pasó en cada deploy  

---

## 🔧 Configuración Inicial

### Paso 1: Limpiar repositorio de archivos sensibles

**CRÍTICO:** Debes eliminar `.env` del tracking de Git.

```powershell
# Ejecutar script de limpieza
.\git-cleanup.ps1
```

O manualmente:

```powershell
# Remover archivos sensibles
git rm --cached .env
git rm -r --cached __pycache__
git rm --cached "*.pyc"

# Commit
git add .gitignore
git commit -m "🔒 Remover archivos sensibles del tracking"
```

### Paso 2: Generar SSH Key para GitHub Actions

```powershell
# En tu máquina local
ssh-keygen -t ed25519 -C "github-actions-convertidor" -f github-actions-key

# Esto genera:
# - github-actions-key       (clave PRIVADA)
# - github-actions-key.pub   (clave PÚBLICA)
```

### Paso 3: Copiar clave pública al servidor

```powershell
# Copiar contenido de la clave pública
Get-Content github-actions-key.pub | clip

# Conectarse al servidor
ssh root@89.116.51.172

# En el servidor, agregar la clave
mkdir -p ~/.ssh
echo "PEGA_AQUI_LA_CLAVE_PUBLICA" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Paso 4: Agregar clave privada a GitHub Secrets

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Nombre: `SSH_PRIVATE_KEY`
5. Valor: Contenido de `github-actions-key` (clave PRIVADA completa)
   ```powershell
   Get-Content github-actions-key
   # Copiar TODO el contenido incluyendo -----BEGIN y -----END
   ```
6. Click **"Add secret"**

### Paso 5: Verificar archivo .env en el servidor

```bash
# En el servidor
ssh root@89.116.51.172

cd /var/www/convertidor

# Verificar que .env existe
ls -la .env

# Si NO existe, crearlo
nano .env
# Pegar configuración desde .env.example y ajustar valores
```

**IMPORTANTE:** El archivo `.env` DEBE existir en el servidor pero NUNCA debe estar en Git.

---

## 🎯 Workflows Disponibles

Tienes DOS workflows en `.github/workflows/`:

### 1️⃣ `deploy.yml` - Deploy con PM2 (Recomendado si ya usas PM2)

**Se activa cuando:**
- Haces push a la rama `main`
- Ejecutas manualmente desde GitHub

**Qué hace:**
1. Compila Tailwind CSS
2. Crea backup en servidor
3. Sincroniza archivos vía rsync
4. Instala dependencias Python
5. Reinicia con PM2

**Usar si:** Ya tienes PM2 configurado (tu caso actual)

### 2️⃣ `deploy-docker.yml` - Deploy con Docker

**Se activa cuando:**
- Cambias archivos en `backend/`, `nginx/` o `docker-compose.yml`
- Ejecutas manualmente desde GitHub

**Qué hace:**
1. Compila CSS
2. Crea backup
3. Sincroniza archivos
4. Reconstruye contenedores Docker
5. Inicia servicios

**Usar si:** Decides migrar a Docker

---

## 🚀 Cómo Funciona el Deploy Automático

### Flujo normal de trabajo:

```powershell
# 1. Hacer cambios en tu código localmente
code backend/app.py

# 2. Compilar CSS (automático en el workflow, pero bueno probarlo)
npm run build-css

# 3. Commit y push
git add .
git commit -m "✨ Nueva funcionalidad"
git push origin main

# 4. ✅ Deploy automático se ejecuta en GitHub
# Ve a: https://github.com/AndresOrtizJDK/Convertidor/actions
```

### Ver progreso del deploy:

1. Ve a tu repo en GitHub
2. Click en **"Actions"** (arriba)
3. Verás el workflow corriendo en tiempo real
4. Click en el job para ver logs detallados

---

## 🔄 Deploy Manual desde GitHub

Si quieres hacer deploy sin push:

1. Ve a **Actions** en GitHub
2. Selecciona el workflow (`Deploy to VPS` o `Deploy with Docker`)
3. Click **"Run workflow"**
4. Selecciona branch `main`
5. Click **"Run workflow"**

---

## 📊 Monitoreo de Deploys

### Ver historial de deploys
```
GitHub → Actions → Deploy to VPS
```

### Logs del deploy
Cada job muestra:
- ✅ Archivos sincronizados
- ✅ Dependencias instaladas
- ✅ Estado de PM2/Docker
- ❌ Errores si los hay

### Notificaciones
GitHub te notificará por email si un deploy falla.

---

## 🛡️ Seguridad

### ✅ Buenas prácticas implementadas:

- ✅ `.env` NUNCA va a Git (está en .gitignore)
- ✅ SSH key solo para GitHub Actions (no reutilizada)
- ✅ Secrets encriptados en GitHub
- ✅ Backups automáticos antes de cada deploy
- ✅ Exclusión de archivos sensibles en rsync

### ⚠️ Cosas a verificar:

```powershell
# Verificar que .env NO esté trackeado
git ls-files | Select-String "\.env$"
# No debe mostrar nada

# Verificar que __pycache__ NO esté trackeado
git ls-files | Select-String "__pycache__"
# No debe mostrar nada
```

---

## 🔧 Personalización

### Cambiar servidor o ruta

Edita `.github/workflows/deploy.yml`:

```yaml
env:
  VPS_HOST: 89.116.51.172  # ← Cambia tu IP aquí
  VPS_USER: root           # ← Cambia usuario aquí
  DEPLOY_PATH: /var/www/convertidor  # ← Cambia ruta aquí
```

### Agregar tests antes del deploy

Edita `.github/workflows/deploy.yml` y agrega antes del deploy:

```yaml
- name: 🧪 Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    python -m pytest tests/
```

### Deploy solo en horarios específicos

```yaml
on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 2 * * *'  # Deploy diario a las 2 AM
```

---

## 🐛 Troubleshooting

### ❌ Error: "Permission denied (publickey)"

**Problema:** La clave SSH no está configurada correctamente.

**Solución:**
```bash
# En el servidor
cat ~/.ssh/authorized_keys | grep github-actions

# Debe mostrar la clave pública
# Si no, agregarla de nuevo
```

### ❌ Error: ".env file not found"

**Problema:** No existe .env en el servidor.

**Solución:**
```bash
ssh root@89.116.51.172
cd /var/www/convertidor
cp .env.example .env
nano .env  # Configurar valores reales
```

### ❌ Error: "PM2 not found"

**Problema:** PM2 no está instalado.

**Solución:**
```bash
ssh root@89.116.51.172
npm install -g pm2
```

### ❌ Deploy exitoso pero app no funciona

**Ver logs en el servidor:**
```bash
ssh root@89.116.51.172
pm2 logs convertidor-flask
# O
cd /var/www/convertidor && docker-compose logs
```

---

## 📋 Checklist Pre-Deploy

Antes de tu primer deploy automático:

- [ ] `.env` removido del tracking de Git
- [ ] `.gitignore` actualizado
- [ ] SSH key generada
- [ ] Clave pública en servidor
- [ ] Secret `SSH_PRIVATE_KEY` en GitHub
- [ ] `.env` existe en servidor (configurado)
- [ ] PM2 o Docker instalado en servidor
- [ ] Probado deploy manual una vez

---

## 🎉 Primer Deploy

```powershell
# 1. Verificar limpieza
.\git-cleanup.ps1

# 2. Push inicial
git add .
git commit -m "🚀 Configurar GitHub Actions deploy"
git push origin main

# 3. Ir a GitHub Actions y ver el magic ✨
# https://github.com/AndresOrtizJDK/Convertidor/actions
```

---

## 📚 Recursos

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [SSH Keys Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Secrets in GitHub](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 🆘 Soporte

Si tienes problemas:

1. **Ver logs del workflow** en GitHub Actions
2. **Ver logs del servidor:**
   ```bash
   ssh root@89.116.51.172 "pm2 logs --lines 100"
   ```
3. **Rollback** a commit anterior:
   ```powershell
   git revert HEAD
   git push origin main  # Deploy automático del rollback
   ```

---

**Última actualización:** Octubre 2025  
**Estado:** ✅ LISTO PARA USAR
