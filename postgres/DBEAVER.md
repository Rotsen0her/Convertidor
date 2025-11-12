# 🦫 Guía de DBeaver para Análisis de Datos

DBeaver es la herramienta ideal para trabajar con 1M+ registros en PostgreSQL.

---

## 📥 Instalación

### Windows / macOS / Linux:
1. Descargar desde: https://dbeaver.io/download/
2. Instalar **DBeaver Community Edition** (gratis)
3. Abrir DBeaver

---

## 🔌 Conexión a PostgreSQL

### Opción 1: Túnel SSH (Recomendado) ✅

1. **Database** → **New Database Connection** → **PostgreSQL**

2. **Pestaña Main:**
   ```
   Host: localhost
   Port: 5433  (o cualquier puerto local libre)
   Database: analytics
   Username: postgres
   Password: [ver archivo .env]
   ```

3. **Pestaña SSH:**
   - ✅ Activar "Use SSH Tunnel"
   ```
   Host/IP: tu-servidor.com
   Port: 22
   Username: root (o tu usuario SSH)
   Authentication: Password o Public Key
   Password: [tu password SSH]
   ```

4. **Test Connection** → **Finish**

---

### Opción 2: Conexión Directa ⚠️

Solo si configuraste firewall UFW para permitir tu IP.

1. **Database** → **New Database Connection** → **PostgreSQL**

2. **Pestaña Main:**
   ```
   Host: tu-servidor.com
   Port: 5432
   Database: analytics
   Username: postgres
   Password: [ver archivo .env]
   ```

3. **Pestaña SSL:**
   - Mode: **require** (recomendado)

4. **Test Connection** → **Finish**

---

## 📊 Features Esenciales de DBeaver

### 1. **Data Viewer** (Ver Datos)
- Doble click en tabla → Ver datos
- **Paginación automática** para millones de filas
- **Filtros rápidos**: Click derecho en columna → Filter
- **Ordenar**: Click en header de columna
- **Exportar**: Click derecho → Export Data → CSV/Excel/JSON

### 2. **SQL Editor** (Ejecutar Queries)
- **Ctrl+Enter** o **Cmd+Enter**: Ejecutar query
- **Ctrl+Shift+E**: Ejecutar todo el script
- **Autocompletado**: Escribir tabla/columna + Tab
- **Formatear SQL**: Ctrl+Shift+F

### 3. **Import Data** (Importar CSV/Excel)
1. Click derecho en tabla → **Import Data**
2. Seleccionar archivo CSV/Excel
3. Mapear columnas automáticamente
4. **Preview** → **Start**
5. DBeaver usa COPY internamente (muy rápido)

### 4. **Export Data** (Exportar Resultados)
1. Ejecutar query
2. En resultados, click derecho → **Export Data**
3. Elegir formato: CSV, Excel, JSON, SQL, HTML
4. Configurar opciones → **Export**

### 5. **ER Diagrams** (Diagramas de Relaciones)
1. Click derecho en Database → **View Diagram**
2. DBeaver genera automáticamente relaciones
3. Útil para entender estructura de datos

### 6. **Data Transfer** (Migrar Datos Entre Bases)
1. **Database** → **Data Transfer**
2. Seleccionar origen y destino
3. Copiar tablas completas entre bases de datos

### 7. **Query History** (Historial de Queries)
- **Ctrl+H**: Ver historial de queries ejecutadas
- Buscar y reutilizar queries anteriores

### 8. **Generate SQL**
- Click derecho en tabla → **Generate SQL** → SELECT/INSERT/UPDATE
- Genera queries automáticamente

---

## 🚀 Workflows para 1M+ Registros

### Workflow 1: Importar CSV Masivo

```sql
-- 1. Crear tabla
CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    producto VARCHAR(255),
    cantidad INTEGER,
    precio DECIMAL(10,2)
);

-- 2. Importar con DBeaver
-- Click derecho en tabla → Import Data → Seleccionar CSV

-- 3. Crear índices DESPUÉS de importar
CREATE INDEX idx_ventas_fecha ON ventas(fecha);
CREATE INDEX idx_ventas_producto ON ventas(producto);

-- 4. Analizar tabla
ANALYZE ventas;
```

### Workflow 2: Análisis Exploratorio

```sql
-- Ver primeras filas
SELECT * FROM ventas LIMIT 100;

-- Contar registros
SELECT COUNT(*) FROM ventas;

-- Estadísticas básicas
SELECT 
    MIN(precio) AS min_precio,
    MAX(precio) AS max_precio,
    AVG(precio)::numeric(10,2) AS avg_precio,
    STDDEV(precio)::numeric(10,2) AS stddev_precio
FROM ventas;

-- Distribución por categoría
SELECT 
    producto,
    COUNT(*) AS cantidad,
    SUM(precio)::numeric(15,2) AS total
FROM ventas
GROUP BY producto
ORDER BY cantidad DESC
LIMIT 20;
```

### Workflow 3: Optimizar Query Lenta

```sql
-- 1. Ver plan de ejecución
EXPLAIN ANALYZE
SELECT * FROM ventas WHERE fecha > '2024-01-01';

-- 2. Si "Seq Scan" aparece, crear índice
CREATE INDEX idx_ventas_fecha ON ventas(fecha);

-- 3. Re-ejecutar EXPLAIN ANALYZE
-- Ahora debería usar "Index Scan"
```

---

## ⚡ Tips de Performance en DBeaver

### 1. **Configurar Result Set Size**
- **Window** → **Preferences** → **Database** → **Result Sets**
- **Result set max size**: 10,000 (evita cargar millones de filas)
- ✅ DBeaver pagina automáticamente

### 2. **Desactivar Fetch All Data**
- En **Preferences** → **Database** → **Result Sets**
- ❌ **Desactivar** "Read all data on fetch"
- Carga datos bajo demanda

### 3. **Usar LIMIT en Queries Exploratorias**
```sql
-- ❌ Malo (intenta cargar todo)
SELECT * FROM ventas;

-- ✅ Bueno
SELECT * FROM ventas LIMIT 1000;
```

### 4. **Cerrar Conexiones No Usadas**
- Cada conexión consume recursos
- Click derecho en conexión → **Disconnect**

### 5. **Aumentar Memoria de DBeaver**
Editar `dbeaver.ini`:
```ini
-Xms256m
-Xmx2048m  # Aumentar a 2GB
```

---

## 📈 Visualizaciones en DBeaver

### Charts Integrados
1. Ejecutar query con agregaciones:
   ```sql
   SELECT 
       DATE_TRUNC('month', fecha) AS mes,
       SUM(cantidad * precio) AS ingresos
   FROM ventas
   GROUP BY mes
   ORDER BY mes;
   ```

2. En resultados: Click derecho → **View Chart**
3. Elegir tipo: Line, Bar, Pie, Scatter

---

## 🔒 Seguridad en DBeaver

### Guardar Contraseñas Seguras
- DBeaver encripta contraseñas localmente
- **Window** → **Preferences** → **Security**
- Configurar Master Password

### Usar Conexiones de Solo Lectura
```sql
-- Crear en PostgreSQL
CREATE USER analyst_readonly WITH PASSWORD 'secure-pass';
GRANT CONNECT ON DATABASE analytics TO analyst_readonly;
GRANT USAGE ON SCHEMA public TO analyst_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_readonly;
```

Luego conectarse con `analyst_readonly` en DBeaver.

---

## 🛠️ Extensiones Útiles

### Activar en DBeaver:
1. **Help** → **Install New Software**
2. Buscar e instalar:
   - **DBeaver Office**: Integración con Excel
   - **DBeaver Git**: Control de versiones de scripts

---

## 🆘 Troubleshooting

### "Connection refused"
- ✅ Verificar túnel SSH está activo
- ✅ PostgreSQL está corriendo: `docker compose ps`
- ✅ Firewall permite puerto 5432

### "Out of Memory"
- ✅ Aumentar `-Xmx` en `dbeaver.ini`
- ✅ Usar LIMIT en queries
- ✅ Desactivar "Read all data on fetch"

### Query muy lenta
- ✅ Usar EXPLAIN ANALYZE
- ✅ Crear índices apropiados
- ✅ Verificar `work_mem` en PostgreSQL

### No puedo importar CSV
- ✅ Verificar encoding (UTF-8)
- ✅ Verificar delimitador (coma vs punto y coma)
- ✅ Verificar que columnas coincidan con tabla

---

## 📚 Recursos Adicionales

- **Documentación DBeaver**: https://dbeaver.com/docs/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **SQL Tutorial**: https://www.postgresqltutorial.com/
- **Performance Tips**: https://wiki.postgresql.org/wiki/Performance_Optimization

---

## 💡 Best Practices

1. ✅ **Siempre usar LIMIT** en queries exploratorias
2. ✅ **Crear índices** antes de análisis pesados
3. ✅ **Ejecutar ANALYZE** después de importaciones
4. ✅ **Usar túnel SSH** para conexiones remotas
5. ✅ **Guardar queries** importantes como SQL scripts
6. ✅ **Exportar resultados** en lugar de copiar/pegar
7. ✅ **Cerrar conexiones** cuando no las uses
8. ✅ **Monitorear queries lentas** con EXPLAIN ANALYZE
9. ✅ **Hacer backups** antes de modificar datos
10. ✅ **Documentar** queries complejas con comentarios
