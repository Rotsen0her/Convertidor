# 🚀 Convertidor - Guía de Deploy

Sistema de transformación de datos con Flask, MySQL y Nginx usando Docker.

## 📋 Requisitos Previos

### En tu máquina local (Windows):
- Docker Desktop (si quieres probar localmente)
- PowerShell
- WSL con rsync instalado
- Node.js y npm (para compilar Tailwind CSS)

### En el VPS:
- Ubuntu 20.04+ / Debian 11+
- Docker y Docker Compose instalados
- Puertos 80 y 443 abiertos
- Dominio apuntando al servidor (opcional, para HTTPS)

## 🔧 Instalación de Requisitos en VPS

```bash
# Conectarse al VPS
ssh root@tu-servidor.com

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Verificar instalación
docker --version
docker-compose --version

# Crear directorio del proyecto
mkdir -p /var/www/convertidor
```

## ⚙️ Configuración Inicial

### 1. Configurar variables de entorno

```powershell
# En tu máquina local
cd "C:\Users\Nestor Hernandez\WebstormProjects\Convertidor"

# Copiar archivo de ejemplo
Copy-Item .env.example .env

# Editar .env con valores reales
notepad .env
```

**Valores que DEBES cambiar en .env:**
```env
MYSQL_ROOT_PASSWORD=tu_password_root_super_seguro
MYSQL_DATABASE=convertidor_db
MYSQL_USER=convertidor_user
MYSQL_PASSWORD=tu_password_usuario_seguro
SECRET_KEY=clave_secreta_muy_larga_y_aleatoria_minimo_32_caracteres
```

### 2. Copiar .env al servidor

```powershell
# Copiar .env al servidor (SOLO la primera vez)
scp .env root@tu-servidor.com:/var/www/convertidor/.env
```

## 🚀 Deploy Automático

### Opción 1: Script PowerShell (Recomendado)

```powershell
# Deploy completo
.\deploy.ps1 -VPS_IP "89.116.51.172" -VPS_USER "root"

# Deploy sin compilar CSS (si ya lo compilaste)
.\deploy.ps1 -VPS_IP "89.116.51.172" -SkipBuild

# Deploy sin hacer backup
.\deploy.ps1 -SkipBackup
```

### Opción 2: Deploy Manual

```powershell
# 1. Compilar Tailwind CSS
npm run build-css

# 2. Sincronizar archivos
$wslPath = wsl wslpath -a (Get-Location)
wsl rsync -avz --progress --delete `
    --exclude 'node_modules' `
    --exclude 'venv' `
    --exclude '__pycache__' `
    --exclude '.git' `
    --exclude '.env' `
    "$wslPath/" root@89.116.51.172:/var/www/convertidor/

# 3. SSH al servidor y ejecutar
ssh root@89.116.51.172

cd /var/www/convertidor

# Detener servicios actuales
docker-compose down

# Construir y levantar
docker-compose build
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## 📊 Gestión del Sistema

### Ver estado de los servicios
```bash
cd /var/www/convertidor
docker-compose ps
```

### Ver logs en tiempo real
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo MySQL
docker-compose logs -f db

# Solo Nginx
docker-compose logs -f nginx
```

### Reiniciar servicios
```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo backend
docker-compose restart backend
```

### Detener y eliminar todo
```bash
docker-compose down

# Detener y eliminar volúmenes (⚠️ ELIMINA LA BASE DE DATOS)
docker-compose down -v
```

## 🔐 Configurar HTTPS con Let's Encrypt

```bash
# Conectarse al servidor
ssh root@tu-servidor.com
cd /var/www/convertidor

# Instalar Certbot
apt install certbot python3-certbot-nginx -y

# Obtener certificado
certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovación automática (ya configurada)
certbot renew --dry-run
```

## 👤 Usuario Admin Inicial

Después del primer deploy, puedes acceder con:

- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambia esta contraseña inmediatamente después del primer login.

## 🔄 Actualizar Aplicación

```powershell
# Desde tu máquina local
.\deploy.ps1 -VPS_IP "89.116.51.172"
```

El script automáticamente:
1. ✅ Compila CSS
2. ✅ Crea backup
3. ✅ Sincroniza archivos
4. ✅ Reconstruye contenedores
5. ✅ Reinicia servicios

## 🐛 Troubleshooting

### El backend no inicia
```bash
# Ver logs detallados
docker-compose logs backend

# Entrar al contenedor
docker-compose exec backend bash

# Verificar variables de entorno
docker-compose exec backend env | grep MYSQL
```

### Error de conexión a MySQL
```bash
# Verificar que MySQL está corriendo
docker-compose ps db

# Verificar logs de MySQL
docker-compose logs db

# Conectarse a MySQL manualmente
docker-compose exec db mysql -u root -p
```

### Problema con permisos de archivos
```bash
# Dar permisos al directorio de cache
docker-compose exec backend chmod -R 755 /tmp/convertidor_cache
```

### CSS no se aplica correctamente
```powershell
# En tu máquina local
npm run build-css

# Sincronizar solo CSS
scp -r static/css root@89.116.51.172:/var/www/convertidor/backend/static/

# Reiniciar nginx
ssh root@89.116.51.172 "cd /var/www/convertidor && docker-compose restart nginx"
```

## 📝 Estructura del Proyecto

```
Convertidor/
├── backend/                  # Aplicación Flask
│   ├── app.py               # Aplicación principal
│   ├── config.py            # Configuración
│   ├── requirements.txt     # Dependencias Python
│   ├── Dockerfile           # Imagen Docker del backend
│   ├── start_gunicorn.sh    # Script de inicio
│   ├── static/              # Archivos estáticos
│   └── templates/           # Templates Jinja2
├── nginx/                   # Configuración Nginx
│   ├── default.conf         # Config del reverse proxy
│   └── Dockerfile           # Imagen Docker de Nginx
├── docker-compose.yml       # Orquestación de servicios
├── init-db.sql             # Script de inicialización DB
├── deploy.ps1              # Script de deploy
├── .env.example            # Ejemplo de variables
└── README_DEPLOY.md        # Esta guía
```

## 🔗 URLs Útiles

- **Aplicación:** http://tu-dominio.com
- **Documentación Docker:** https://docs.docker.com
- **Documentación Flask:** https://flask.palletsprojects.com

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica las variables de entorno en `.env`
3. Asegúrate de que los puertos 80 y 443 estén abiertos
4. Verifica que Docker esté corriendo: `docker ps`

---

**Última actualización:** Octubre 2025
