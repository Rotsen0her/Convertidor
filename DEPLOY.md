# 🚀 Guía de Deploy - Convertidor

## 📋 Pre-requisitos en el VPS

- Ubuntu/Debian 20.04+
- Docker y Docker Compose instalados
- Dominio apuntando al VPS (ejemplo: convertidor.zynapzys.com)
- Puertos 80 y 443 abiertos

## 🛠️ Instalación de Docker (si no está instalado)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker compose -y

# Reiniciar sesión para aplicar cambios
```

## 📥 Deploy Paso a Paso

### 1. Clonar el repositorio

```bash
cd /var/www
sudo git clone https://github.com/Rotsen0her/Convertidor.git
cd Convertidor
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus valores
nano .env
```

**Importante:** Cambia TODOS los valores:
- `SECRET_KEY`: Genera una clave aleatoria segura
- `MYSQL_ROOT_PASSWORD`: Contraseña fuerte para root de MySQL
- `MYSQL_PASSWORD`: Contraseña fuerte para el usuario de la app

### 3. Ajustar permisos

```bash
sudo chown -R $USER:$USER /var/www/Convertidor
chmod +x backend/start_gunicorn.sh
chmod +x deploy.sh
```

### 4. Actualizar server_name en Nginx

```bash
nano nginx/default.conf
```

Cambia `server_name` a tu dominio:
```nginx
server_name tu-dominio.com www.tu-dominio.com;
```

### 5. Levantar contenedores

```bash
# Primera vez (construye las imágenes)
docker compose up -d --build

# Ver logs en tiempo real
docker compose logs -f

# Verificar que todo esté corriendo
docker compose ps
```

### 6. Verificar base de datos

```bash
# Entrar al contenedor de MySQL
docker compose exec db mysql -u root -p

# Dentro de MySQL:
USE zafiro_bi;
SHOW TABLES;
SELECT * FROM usuarios;
exit;
```

### 7. Configurar HTTPS con Certbot (Opcional pero recomendado)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado (el contenedor Nginx debe estar corriendo)
docker compose exec nginx certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovación automática
sudo crontab -e
# Agregar línea:
0 3 * * * docker compose -f /var/www/Convertidor/docker compose.yml exec nginx certbot renew --quiet
```

## 🔄 Actualizar la aplicación

Cuando hagas cambios en el código:

```bash
cd /var/www/Convertidor

# Usar el script de deploy automático
./deploy.sh

# O manualmente:
git pull origin main
docker compose down
docker compose up -d --build
```

## 🧪 Verificar funcionamiento

1. **Verificar contenedores:**
   ```bash
   docker compose ps
   ```
   Todos deben estar "Up"

2. **Verificar logs:**
   ```bash
   docker compose logs backend
   docker compose logs nginx
   docker compose logs db
   ```

3. **Acceder a la aplicación:**
   - HTTP: `http://tu-dominio.com`
   - HTTPS: `https://tu-dominio.com` (después de Certbot)

4. **Login por defecto:**
   - Usuario: `admin`
   - Contraseña: `admin123` (cambiar inmediatamente)

## 🔧 Comandos útiles

```bash
# Ver logs en vivo
docker compose logs -f backend

# Reiniciar un servicio específico
docker compose restart backend

# Detener todo
docker compose down

# Detener y eliminar volúmenes (⚠️ CUIDADO: elimina la base de datos)
docker compose down -v

# Ver uso de recursos
docker stats

# Entrar al contenedor backend
docker compose exec backend bash

# Backup de base de datos
docker compose exec db mysqldump -u root -p zafiro_bi > backup_$(date +%Y%m%d).sql
```

## 🔐 Cambiar contraseña de admin

Opción 1 - Usando el script:
```bash
chmod +x reset-admin.sh
./reset-admin.sh
```

Opción 2 - Manualmente desde Python:
```bash
docker compose exec backend python3 -c "
from werkzeug.security import generate_password_hash
print(generate_password_hash('tu_nueva_contraseña'))
"
# Copiar el hash generado y actualizarlo en la base de datos
```

## 🐛 Solución de problemas comunes

### Puerto 80 ya en uso
```bash
# Ver qué está usando el puerto
sudo lsof -i :80
sudo systemctl stop apache2  # o nginx si hay uno instalado
```

### Base de datos no se conecta
```bash
# Verificar que el contenedor db esté corriendo
docker compose ps db

# Ver logs de MySQL
docker compose logs db

# Verificar variables de entorno
docker compose exec backend env | grep MYSQL
```

### Permisos de archivos
```bash
# Dar permisos a directorios de uploads
docker compose exec backend mkdir -p uploads transformados
docker compose exec backend chmod 755 uploads transformados
```

## 📊 Monitoreo

Recomendaciones para producción:
- Configurar backups automáticos de la base de datos
- Usar un sistema de monitoreo (ej: Uptime Robot)
- Revisar logs regularmente
- Mantener Docker y el sistema actualizado

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs: `docker compose logs`
2. Verifica la configuración del `.env`
3. Asegúrate de que los puertos estén abiertos
4. Revisa la configuración del dominio/DNS

---

**¡Listo para producción! 🎉**
