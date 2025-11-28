# Configuración de Nginx Proxy Manager para Archivos Grandes

## Problema Resuelto
- **Error**: "Unexpected token • e, `<html>` is not valid JSON"
- **Causa**: Timeouts y límites de memoria insuficientes para archivos de 250MB + 30MB
- **Solución**: Aumento de timeouts, memoria y configuración de Nginx

## Cambios Realizados

### 1. Backend (Gunicorn)
- ✅ Timeout aumentado de 600s a 3600s (1 hora)
- ✅ Workers aumentados de 3 a 4
- ✅ Configurado auto-reinicio de workers cada 100 requests
- ✅ Usar /dev/shm para mejor rendimiento

### 2. Docker
- ✅ Memoria aumentada de 1GB a 3GB
- ✅ CPU aumentada de 1 a 2 cores
- ✅ Reserva de 1GB garantizada

### 3. Flask
- ✅ MAX_CONTENT_LENGTH aumentado de 1GB a 2GB

### 4. PostgreSQL
- ✅ shared_buffers: 256MB → 512MB
- ✅ work_mem: 16MB → 32MB
- ✅ maintenance_work_mem: 64MB → 128MB
- ✅ effective_cache_size: 512MB → 1GB

### 5. Nginx Proxy Manager
⚠️ **IMPORTANTE**: Debes configurar manualmente en la interfaz web de NPM

## Instrucciones para Nginx Proxy Manager

### Opción A: Configuración por Proxy Host (Recomendado)

1. Accede a Nginx Proxy Manager en `http://localhost:81`
   - Usuario: `admin@example.com`
   - Contraseña: `changeme` (cambiar en primer acceso)

2. Ve a "Proxy Hosts" y selecciona tu host del convertidor

3. En la pestaña "Advanced", agrega esta configuración:

```nginx
# Timeouts para archivos grandes
proxy_connect_timeout 3600s;
proxy_send_timeout 3600s;
proxy_read_timeout 3600s;
send_timeout 3600s;

# Tamaño máximo de carga (2GB)
client_max_body_size 2000M;

# Buffers para archivos grandes
client_body_buffer_size 256k;
proxy_buffering off;
proxy_request_buffering off;

# Headers adicionales
proxy_http_version 1.1;
proxy_set_header Connection "";
```

4. Guarda los cambios

### Opción B: Configuración Global

Si tienes múltiples hosts que necesitan estas configuraciones:

1. Accede al contenedor de NPM:
```powershell
docker exec -it convertidor_npm /bin/bash
```

2. Edita el archivo de configuración principal:
```bash
nano /data/nginx/custom/http_top.conf
```

3. Agrega el contenido del archivo `custom-nginx.conf`

4. Sal del contenedor y reinicia:
```powershell
docker restart convertidor_npm
```

## Aplicar los Cambios

Después de realizar los cambios, reinicia los contenedores:

```powershell
cd "c:\Users\andre\Music\pagina web\Convertidor"

# Detener servicios
docker-compose down

# Reconstruir backend con nueva configuración
docker-compose build backend

# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f backend
```

## Verificar que Funciona

1. Los logs de Gunicorn deben mostrar:
```
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: gevent
[INFO] Booting worker with pid: XX
```

2. Procesamiento de archivos grandes debe tomar más tiempo pero completarse sin errores

3. No deberías ver más el error "is not valid JSON"

## Monitoreo

Ver logs en tiempo real:
```powershell
# Backend
docker logs -f convertidor_backend

# Nginx Proxy Manager
docker logs -f convertidor_npm

# Base de datos
docker logs -f convertidor_db
```

## Troubleshooting

Si sigues viendo errores:

1. **Verifica timeouts en NPM**: El paso más crítico es la configuración manual en NPM

2. **Verifica memoria disponible**:
```powershell
docker stats
```

3. **Aumenta más si es necesario**: Edita `docker-compose.yml` y cambia `memory: 3G` a `memory: 4G` o más

4. **Verifica el proceso completo**:
```powershell
# Ver si los archivos se están procesando
docker exec -it convertidor_backend ls -lh /tmp/

# Ver memoria usada por Python
docker exec -it convertidor_backend ps aux
```

## Notas Importantes

- El procesamiento de 250MB + 30MB puede tardar **varios minutos**
- El navegador debe esperar sin timeout (el nuevo timeout es 1 hora)
- Si falla una vez, puede que el worker necesite reiniciarse (hace esto automáticamente cada 100 requests)
- Considera dividir archivos muy grandes si es posible

## Configuración Alternativa (Si No Usas NPM)

Si usas Nginx standalone, crea `/etc/nginx/conf.d/convertidor.conf`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    # Configuración para archivos grandes
    client_max_body_size 2000M;
    client_body_timeout 3600s;
    client_header_timeout 3600s;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;
        send_timeout 3600s;
        
        proxy_buffering off;
        proxy_request_buffering off;
        
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
