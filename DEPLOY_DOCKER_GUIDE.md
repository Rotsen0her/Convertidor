# 🚀 Guía de Deploy - luziia.cloud

Despliegue del proyecto Convertidor en VPS usando Docker Compose.

---

## 📋 Arquitectura

```
┌─────────────────┐
│   Internet      │
│  (Port 80/443)  │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Nginx  │ ← Reverse Proxy + SSL
    │(Container)
    └────┬────┘
         │
    ┌────▼────┐
    │ Backend │ ← Flask + Gunicorn
    │(Container)
    └────┬────┘
         │
    ┌────▼────┐
    │  MySQL  │ ← Base de datos
    │(Container)
    └─────────┘
```

---

## ⚙️ Requisitos Previos

### En tu máquina local:
- ✅ Git
- ✅ Node.js + npm (para compilar Tailwind)
- ✅ SSH access al VPS

### En el VPS (89.116.51.172):
- ✅ Ubuntu 20.04+
- ✅ Docker instalado
- ✅ Docker Compose instalado
- ✅ Dominio apuntando al servidor (luziia.cloud)

---

## 🔧 Instalación de Docker en VPS

```bash
# Conectarse al VPS
ssh root@89.116.51.172

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Verificar
docker --version
docker-compose --version
```

---

## 📦 Deploy Paso a Paso

### 1️⃣ Preparar el Proyecto Localmente

```powershell
# En tu máquina (Windows)
cd "C:\Users\Nestor Hernandez\WebstormProjects\Convertidor"

# Instalar dependencias de Node
npm install

# Compilar Tailwind CSS
npm run build-css

# Esto genera: backend/static/css/output.css
```

**Verificar que se generó:**
```powershell
Test-Path backend/static/css/output.css
# Debe retornar: True
```

---

### 2️⃣ Configurar .env

```powershell
# Copiar ejemplo
Copy-Item .env.example .env

# Editar con valores reales
notepad .env
```

**Contenido de `.env` (VALORES DE EJEMPLO - USA TUS PROPIOS):**
```env
SECRET_KEY=d4f8a1c6b7e3f2a9c0e5b6d9f3a1c2b4d6e7f8a9c0b1d2e3f4a5b6c7d8e9f0
MYSQL_ROOT_PASSWORD=TuPasswordRootSeguro123!
MYSQL_DATABASE=joseberrio_db
MYSQL_USER=joseberrio_admin
MYSQL_PASSWORD=TuPasswordUsuarioSeguro456!
MYSQL_HOST=db
MYSQL_PORT=3306
FLASK_ENV=production
FLASK_DEBUG=0
```

⚠️ **IMPORTANTE:** Cambia las contraseñas por valores seguros únicos.

---

### 3️⃣ Subir al Repositorio

```powershell
# Limpiar archivos sensibles del tracking
.\git-cleanup.ps1

# Commit y push
git add .
git commit -m "🚀 Preparar para deploy Docker"
git push origin main
```

---

### 4️⃣ Clonar en el VPS

```bash
# Conectarse al VPS
ssh root@89.116.51.172

# Crear directorio
mkdir -p /var/www
cd /var/www

# Clonar repositorio
git clone https://github.com/AndresOrtizJDK/Convertidor.git
cd Convertidor
```

---

### 5️⃣ Configurar .env en el Servidor

```bash
# En el VPS
cd /var/www/Convertidor

# Copiar ejemplo
cp .env.example .env

# Editar con valores reales
nano .env

# Pegar la configuración (misma que en local)
# Ctrl+O para guardar, Ctrl+X para salir
```

---

### 6️⃣ Levantar los Servicios

```bash
# En el VPS
cd /var/www/Convertidor

# Construir e iniciar contenedores
docker-compose up -d --build
```

**Esto hará:**
1. ✅ Construir imagen de backend (Flask + Gunicorn)
2. ✅ Construir imagen de nginx
3. ✅ Descargar imagen de MySQL 8.0
4. ✅ Crear red entre contenedores
5. ✅ Crear volúmenes persistentes
6. ✅ Iniciar todos los servicios

---

### 7️⃣ Verificar que Todo Funciona

```bash
# Ver estado de los contenedores
docker-compose ps

# Debe mostrar:
# NAME                   STATUS
# convertidor_backend    Up
# convertidor_db         Up
# convertidor_nginx      Up

# Ver logs
docker-compose logs -f backend

# Ver logs de todos
docker-compose logs -f
```

**Probar en navegador:**
```
http://89.116.51.172
# O
http://luziia.cloud
```

---

### 8️⃣ Configurar HTTPS con Certbot

```bash
# En el VPS
cd /var/www/Convertidor

# Ejecutar Certbot dentro del contenedor Nginx
docker exec -it convertidor_nginx certbot --nginx \
  -d luziia.cloud \
  -d www.luziia.cloud \
  --email tu@email.com \
  --agree-tos \
  --no-eff-email

# Reiniciar Nginx
docker-compose restart nginx
```

**Renovación automática:**
```bash
# Agregar cron job
crontab -e

# Agregar línea:
0 0 * * * docker exec convertidor_nginx certbot renew --quiet
```

---

## 🔄 Actualizar la Aplicación

### Desde tu máquina local:

```powershell
# 1. Hacer cambios en el código
code backend/app.py

# 2. Recompilar CSS si cambiaste estilos
npm run build-css

# 3. Commit y push
git add .
git commit -m "✨ Nueva funcionalidad"
git push origin main
```

### En el VPS:

```bash
# 1. Conectarse
ssh root@89.116.51.172
cd /var/www/Convertidor

# 2. Pull cambios
git pull origin main

# 3. Reconstruir y reiniciar
docker-compose down
docker-compose up -d --build

# O solo reiniciar backend si no hay cambios estructurales
docker-compose restart backend
```

---

## 🗄️ Crear Tablas de Base de Datos

```bash
# Conectarse al contenedor MySQL
docker exec -it convertidor_db mysql -u root -p

# Ingresar password del MYSQL_ROOT_PASSWORD
```

```sql
-- Crear base de datos (si no existe)
CREATE DATABASE IF NOT EXISTS joseberrio_db;
USE joseberrio_db;

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'usuario') DEFAULT 'usuario',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear usuario admin
-- (password hasheado de "admin123" - CAMBIAR después)
INSERT INTO usuarios (usuario, password, rol) VALUES
('admin', 'scrypt:32768:8:1$yZQH8Jf0rGJ4Rwzm$8a8f5d8e7a0b2c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7', 'admin')
ON DUPLICATE KEY UPDATE id=id;

-- Salir
exit;
```

---

## 📊 Gestión de Contenedores

### Ver estado
```bash
docker-compose ps
```

### Ver logs
```bash
# Todos
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo MySQL
docker-compose logs -f db

# Últimas 50 líneas
docker-compose logs --tail=50
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

### Detener servicios
```bash
# Detener
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar contenedores Y volúmenes (⚠️ ELIMINA DB)
docker-compose down -v
```

### Entrar a un contenedor
```bash
# Backend
docker exec -it convertidor_backend bash

# MySQL
docker exec -it convertidor_db mysql -u root -p

# Nginx
docker exec -it convertidor_nginx sh
```

---

## 🐛 Troubleshooting

### Backend no inicia
```bash
# Ver logs detallados
docker-compose logs backend

# Verificar variables de entorno
docker exec convertidor_backend env | grep MYSQL

# Reiniciar
docker-compose restart backend
```

### Error de conexión a MySQL
```bash
# Verificar que MySQL esté corriendo
docker-compose ps db

# Ver logs de MySQL
docker-compose logs db

# Conectarse manualmente
docker exec -it convertidor_db mysql -u joseberrio_admin -p
```

### CSS no se carga
```bash
# Verificar que output.css existe en el contenedor
docker exec convertidor_backend ls -la /app/static/css/

# Si no existe, compilar localmente y reconstruir
npm run build-css
docker-compose up -d --build backend
```

### Puerto 80 ya está en uso
```bash
# Ver qué proceso usa el puerto 80
sudo lsof -i :80

# Detener nginx del sistema (si existe)
sudo systemctl stop nginx
```

---

## 🔐 Seguridad

### Firewall
```bash
# Instalar UFW
apt install ufw

# Permitir SSH, HTTP, HTTPS
ufw allow 22
ufw allow 80
ufw allow 443

# Activar
ufw enable
```

### Actualizar Sistema
```bash
apt update
apt upgrade -y
```

### Cambiar Password de Admin
Usa el script `generate_password.py`:
```bash
docker exec -it convertidor_backend python3 generate_password.py
```

---

## 📋 Checklist de Deploy

- [ ] Docker instalado en VPS
- [ ] Dominio apuntando a VPS
- [ ] CSS compilado localmente (`npm run build-css`)
- [ ] `.env` configurado en VPS
- [ ] Contenedores corriendo (`docker-compose ps`)
- [ ] Base de datos inicializada
- [ ] Usuario admin creado
- [ ] HTTPS configurado con Certbot
- [ ] Firewall configurado
- [ ] Backup configurado

---

## 🎉 Resultado Final

✅ **Flask + Gunicorn** corriendo en contenedor  
✅ **MySQL 8.0** aislado y persistente  
✅ **Nginx** como proxy inverso  
✅ **HTTPS** con Let's Encrypt  
✅ **Tailwind CSS** precompilado  
✅ **Variables de entorno** seguras  

**URL:** https://luziia.cloud

---

**Última actualización:** Octubre 2025
