# 🛠️ Comandos Útiles - Convertidor

## 📦 Desarrollo Local

### Instalar dependencias
```powershell
# Node/Tailwind
npm install

# Python (con virtualenv)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### Compilar CSS
```powershell
# Una vez
npm run build-css

# Modo watch (compila automáticamente al guardar)
npm run watch-css
```

### Ejecutar localmente
```powershell
# Con virtualenv activado
cd backend
python app.py

# La app estará en http://127.0.0.1:5000
```

---

## 🚀 Deploy

### Deploy completo (Docker)
```powershell
.\deploy.ps1 -VPS_IP "89.116.51.172"
```

### Deploy completo (PM2)
```powershell
.\deploy-pm2.ps1 -VPS_IP "89.116.51.172"
```

### Deploy sin compilar CSS
```powershell
.\deploy.ps1 -SkipBuild
```

### Deploy sin backup
```powershell
.\deploy.ps1 -SkipBackup
```

### Deploy solo sincronizar archivos (sin reiniciar)
```powershell
.\deploy-pm2.ps1 -SkipRestart
```

---

## 🐳 Docker (en el VPS)

### Ver estado
```bash
cd /var/www/convertidor
docker-compose ps
```

### Ver logs
```bash
# Todos
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo base de datos
docker-compose logs -f db

# Últimas 100 líneas
docker-compose logs --tail=100
```

### Reiniciar servicios
```bash
# Todo
docker-compose restart

# Solo backend
docker-compose restart backend

# Solo nginx
docker-compose restart nginx
```

### Entrar a un contenedor
```bash
# Backend
docker-compose exec backend bash

# Base de datos
docker-compose exec db mysql -u root -p
```

### Reconstruir imágenes
```bash
# Reconstruir todo
docker-compose build

# Reconstruir sin cache
docker-compose build --no-cache

# Reconstruir y reiniciar
docker-compose up -d --build
```

### Limpiar todo y empezar de cero
```bash
# ⚠️ ESTO ELIMINA LA BASE DE DATOS
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔧 PM2 (en el VPS)

### Ver estado
```bash
pm2 list
pm2 status
```

### Ver logs
```bash
# En tiempo real
pm2 logs convertidor-flask

# Últimas 100 líneas
pm2 logs convertidor-flask --lines 100

# Solo errores
pm2 logs convertidor-flask --err

# Limpiar logs antiguos
pm2 flush
```

### Reiniciar
```bash
# Reinicio graceful (sin downtime)
pm2 reload convertidor-flask

# Reinicio hard
pm2 restart convertidor-flask

# Detener
pm2 stop convertidor-flask

# Iniciar
pm2 start convertidor-flask
```

### Monitoreo
```bash
# Dashboard en tiempo real
pm2 monit

# Información detallada
pm2 show convertidor-flask

# Uso de recursos
pm2 ls
```

### Configuración
```bash
# Guardar configuración actual
pm2 save

# Iniciar PM2 al arrancar el servidor
pm2 startup

# Eliminar de inicio automático
pm2 unstartup
```

---

## 🗄️ Base de Datos

### Con Docker:
```bash
# Conectarse a MySQL
docker-compose exec db mysql -u root -p

# Backup
docker-compose exec db mysqldump -u root -p convertidor_db > backup.sql

# Restaurar
docker-compose exec -T db mysql -u root -p convertidor_db < backup.sql

# Ver tablas
docker-compose exec db mysql -u root -p -e "USE convertidor_db; SHOW TABLES;"
```

### Con MySQL local:
```bash
# Conectarse
mysql -u root -p

# Backup
mysqldump -u root -p convertidor_db > backup.sql

# Restaurar
mysql -u root -p convertidor_db < backup.sql
```

### Queries útiles:
```sql
-- Ver usuarios
USE convertidor_db;
SELECT id, usuario, rol FROM usuarios;

-- Crear usuario
INSERT INTO usuarios (usuario, password, rol) 
VALUES ('nuevo_usuario', 'hash_aqui', 'usuario');

-- Cambiar contraseña (usar generate_password.py primero)
UPDATE usuarios SET password = 'nuevo_hash' WHERE usuario = 'admin';

-- Cambiar rol
UPDATE usuarios SET rol = 'admin' WHERE usuario = 'nombre_usuario';

-- Eliminar usuario
DELETE FROM usuarios WHERE id = 123;
```

---

## 📁 Archivos y Permisos (en el VPS)

### Verificar permisos
```bash
ls -la /var/www/convertidor
ls -la /tmp/convertidor_cache
```

### Corregir permisos
```bash
# Directorios
chmod 755 /var/www/convertidor
chmod 755 /tmp/convertidor_cache

# Scripts
chmod +x /var/www/convertidor/start_gunicorn.sh

# .env (solo lectura del propietario)
chmod 600 /var/www/convertidor/.env
```

### Ver espacio en disco
```bash
df -h
du -sh /var/www/convertidor
du -sh /tmp/convertidor_cache
```

### Limpiar cache
```bash
# Limpiar cache de archivos procesados
rm -rf /tmp/convertidor_cache/*

# Con Docker
docker-compose exec backend rm -rf /tmp/convertidor_cache/*
```

---

## 🔍 Debugging

### Ver si la app está corriendo
```bash
# Ver procesos Python
ps aux | grep gunicorn
ps aux | grep python

# Ver puertos abiertos
netstat -tlnp | grep 8000
ss -tlnp | grep 8000
```

### Probar conexión a la app
```bash
# Desde el servidor
curl http://localhost:8000

# Desde fuera
curl http://tu-servidor.com
```

### Ver errores recientes
```bash
# Con Docker
docker-compose logs --tail=50 backend | grep ERROR

# Con PM2
pm2 logs convertidor-flask --err --lines 50

# Logs del sistema
journalctl -u nginx -n 50
```

### Test de conectividad MySQL
```bash
# Con Docker
docker-compose exec backend python3 -c "from flask_mysqldb import MySQL; print('OK')"

# Sin Docker
cd /var/www/convertidor
source venv/bin/activate
python3 -c "from flask_mysqldb import MySQL; print('OK')"
```

---

## 🔐 Seguridad

### Generar SECRET_KEY aleatoria
```powershell
# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

```bash
# Bash
openssl rand -hex 32
```

### Generar hash de contraseña
```bash
cd /var/www/convertidor
python3 generate_password.py
```

### Verificar .env no tiene CRLF
```bash
file .env
# Debe decir: ASCII text, no "with CRLF"

# Corregir si tiene CRLF
sed -i 's/\r$//' .env
```

---

## 🌐 Nginx

### Recargar configuración
```bash
# Con Docker
docker-compose restart nginx

# Sin Docker
sudo nginx -t              # Verificar sintaxis
sudo systemctl reload nginx
```

### Ver logs de Nginx
```bash
# Con Docker
docker-compose logs nginx

# Sin Docker
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔄 Actualización Rápida

### Solo actualizar código (sin reinstalar dependencias)
```powershell
# Sincronizar solo archivos .py
$wslPath = wsl wslpath -a (Get-Location)
wsl rsync -avz --progress `
    --include '*.py' `
    --include '*.html' `
    --include '*.css' `
    --exclude '*' `
    "$wslPath/backend/" root@89.116.51.172:/var/www/convertidor/

# Reiniciar
ssh root@89.116.51.172 "pm2 reload convertidor-flask"
```

### Solo actualizar CSS
```powershell
npm run build-css
scp -r static/css root@89.116.51.172:/var/www/convertidor/backend/static/
```

### Solo actualizar templates
```powershell
$wslPath = wsl wslpath -a (Get-Location)
wsl rsync -avz --progress `
    "$wslPath/backend/templates/" root@89.116.51.172:/var/www/convertidor/templates/
ssh root@89.116.51.172 "pm2 reload convertidor-flask"
```

---

## 📊 Monitoreo de Recursos

### Uso de CPU y RAM
```bash
# General
top
htop

# Solo Docker
docker stats

# Solo procesos Python
ps aux | grep python | awk '{print $2, $3, $4, $11}'
```

### Espacio en disco
```bash
df -h
du -sh /var/www/convertidor
du -sh /var/lib/docker  # Si usas Docker
```

---

## 🆘 Emergencias

### La app no responde
```bash
# Ver qué está pasando
pm2 logs convertidor-flask --lines 100

# O con Docker
docker-compose logs backend --tail=100

# Reinicio hard
pm2 restart convertidor-flask
# O
docker-compose restart backend
```

### Error de conexión a MySQL
```bash
# Verificar que MySQL esté corriendo
docker-compose ps db
# O
systemctl status mysql

# Ver logs de MySQL
docker-compose logs db
```

### Disco lleno
```bash
# Ver qué ocupa más espacio
du -sh /* | sort -hr | head -10

# Limpiar logs antiguos
pm2 flush
docker system prune -a

# Limpiar cache
rm -rf /tmp/convertidor_cache/*
```

### Rollback rápido
```bash
# Restaurar backup
cd /var/www
mv convertidor convertidor_broken
tar -xzf /tmp/convertidor_backup_20251004_120000.tar.gz
pm2 restart convertidor-flask
```

---

**Última actualización:** Octubre 2025
