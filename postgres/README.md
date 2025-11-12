# 🗄️ PostgreSQL para Análisis de Datos

Base de datos PostgreSQL configurada para análisis de datos con 1M+ registros.

---

## 🔐 Opciones de Acceso

### **Opción 1: Túnel SSH (RECOMENDADO)** ✅

La forma más segura. El puerto 5432 solo escucha en localhost del servidor.

#### En tu máquina local:
```bash
ssh -L 5433:127.0.0.1:5432 root@tu-servidor.com -N
```

#### Configuración DBeaver:
```
Host: localhost
Port: 5433
Database: analytics
Username: postgres
Password: [ver archivo .env]
```

**Ventajas:**
- ✅ Puerto no expuesto a internet
- ✅ Doble autenticación (SSH + DB)
- ✅ Conexión cifrada

---

### **Opción 2: Acceso Directo con Firewall** ⚠️

Solo si necesitas acceso sin túnel SSH.

#### 1. Modificar `docker-compose.yml`:
```yaml
ports:
  - "0.0.0.0:5432:5432"  # En lugar de 127.0.0.1:5432:5432
```

#### 2. Configurar Firewall UFW (Ubuntu):
```bash
# Permitir solo IPs específicas
sudo ufw allow from TU_IP_CLIENTE to any port 5432 proto tcp
sudo ufw enable

# Ver reglas
sudo ufw status
```

#### 3. Configuración DBeaver:
```
Host: tu-servidor.com
Port: 5432
Database: analytics
Username: postgres
Password: [ver archivo .env]
SSL: Require (recomendado)
```

---

## 🚀 Configuración Inicial

### 1. Variables de entorno ya configuradas (`.env`):
```env
POSTGRES_DB=analytics           # Base de datos por defecto
POSTGRES_USER=postgres          # Usuario administrador
POSTGRES_PASSWORD=***           # Contraseña segura

# Optimizaciones para 1M+ registros
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_WORK_MEM=16MB
POSTGRES_MAINTENANCE_WORK_MEM=64MB
```

### 2. Desplegar/Actualizar:
```bash
cd postgres
docker compose up -d
```

### 3. Ver logs:
```bash
docker compose logs -f postgres
```

---

## 📊 Conectar con DBeaver

### Instalación:
- **Descargar:** https://dbeaver.io/download/
- **Gratis:** Community Edition

### Crear Conexión:
1. **New Database Connection** → PostgreSQL
2. Ingresar datos según la opción de acceso elegida
3. **Test Connection**
4. **Finish**

### Features útiles en DBeaver:
- ✅ **Data Transfer**: Importar CSV/Excel masivamente
- ✅ **ER Diagrams**: Visualizar relaciones
- ✅ **SQL Editor**: Con autocompletado
- ✅ **Export Data**: A múltiples formatos
- ✅ **Query History**: Historial de consultas
- ✅ **Data Viewer**: Tablas con millones de filas

---

## 🔧 Optimizaciones para 1M+ Registros

### Índices (ejemplo):
```sql
-- Crear índice en columna frecuentemente consultada
CREATE INDEX idx_tabla_columna ON mi_tabla(columna);

-- Índice compuesto
CREATE INDEX idx_tabla_col1_col2 ON mi_tabla(col1, col2);

-- Analizar tabla después de importar datos masivos
ANALYZE mi_tabla;
```

### Importación masiva de datos:
```sql
-- Desde DBeaver o psql
\COPY mi_tabla FROM '/ruta/datos.csv' WITH (FORMAT csv, HEADER true);

-- O desde DBeaver: Right-click tabla → Import Data
```

### Monitoreo de queries lentas:
```sql
-- Ver queries activas
SELECT pid, query, state, query_start 
FROM pg_stat_activity 
WHERE state != 'idle';

-- Ver queries más lentas (requiere pg_stat_statements)
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 🔒 Usuario de Solo Lectura (Opcional)

Si quieres dar acceso limitado a analistas:

```sql
-- Conectarse como postgres
CREATE USER analyst WITH PASSWORD 'secure-password-here';

-- Permisos de solo lectura
GRANT CONNECT ON DATABASE analytics TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst;
```

---

## 📈 Recursos Asignados

- **CPU**: 2 cores (aumentado para análisis)
- **RAM**: 2GB límite, 512MB reservados
- **Shared Buffers**: 256MB (caché de PostgreSQL)
- **Work Mem**: 16MB por operación de ordenamiento/join
- **Maintenance Work Mem**: 64MB para VACUUM, CREATE INDEX

---

## 🛠️ Comandos Útiles

```bash
# Backup completo
docker compose exec postgres pg_dump -U postgres analytics > backup.sql

# Restaurar backup
cat backup.sql | docker compose exec -T postgres psql -U postgres analytics

# Conectarse con psql
docker compose exec postgres psql -U postgres -d analytics

# Ver tamaño de base de datos
docker compose exec postgres psql -U postgres -c "\l+"

# Ver tamaño de tablas
docker compose exec postgres psql -U postgres analytics -c "\dt+"
```

---

## 🎯 Recomendaciones para el Cliente

1. **Usar DBeaver** para análisis visual de datos
2. **Crear índices** en columnas frecuentemente consultadas
3. **Usar EXPLAIN ANALYZE** para optimizar queries lentas
4. **Particionar tablas** si superan 10M de registros
5. **Hacer VACUUM** periódicamente para mantener performance

---

## 🆘 Troubleshooting

### Conexión rechazada:
```bash
# Verificar que PostgreSQL esté corriendo
docker compose ps

# Ver logs
docker compose logs postgres

# Verificar puerto
netstat -tulpn | grep 5432
```

### Query muy lenta:
```sql
-- Analizar plan de ejecución
EXPLAIN ANALYZE SELECT * FROM mi_tabla WHERE columna = 'valor';

-- Crear índice si falta
CREATE INDEX idx_columna ON mi_tabla(columna);
```

### Disco lleno:
```bash
# Ver uso de disco
du -sh db_data/

# Limpiar datos antiguos
docker compose exec postgres vacuumdb -U postgres --full --analyze analytics
```
