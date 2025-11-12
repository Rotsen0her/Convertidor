-- ============================================
-- QUERIES ÚTILES PARA ANÁLISIS DE DATOS
-- PostgreSQL Analytics Database
-- ============================================

-- ============================================
-- 1. INFORMACIÓN DEL SISTEMA
-- ============================================

-- Ver versión de PostgreSQL
SELECT version();

-- Ver tamaño de base de datos
SELECT 
    pg_database.datname AS database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;

-- Ver tamaño de tablas (ordenadas por tamaño)
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size,
    pg_stat_user_tables.n_live_tup AS row_count
FROM pg_tables
JOIN pg_stat_user_tables ON pg_tables.tablename = pg_stat_user_tables.tablename
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Ver índices de una tabla
SELECT
    tablename,
    indexname,
    indexdef,
    pg_size_pretty(pg_relation_size(indexrelid::regclass)) AS index_size
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- ============================================
-- 2. OPTIMIZACIÓN DE QUERIES
-- ============================================

-- Ver queries lentas actualmente en ejecución
SELECT 
    pid,
    now() - query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE state != 'idle'
    AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;

-- Ver estadísticas de queries (requiere pg_stat_statements)
SELECT 
    calls,
    total_exec_time::numeric(10,2) AS total_time_ms,
    mean_exec_time::numeric(10,2) AS avg_time_ms,
    max_exec_time::numeric(10,2) AS max_time_ms,
    LEFT(query, 100) AS query_snippet
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Analizar plan de ejecución de una query (ejemplo)
EXPLAIN ANALYZE
SELECT * FROM tu_tabla WHERE columna = 'valor';

-- ============================================
-- 3. MANTENIMIENTO Y MONITOREO
-- ============================================

-- Verificar salud de índices (bloat)
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid::regclass)) AS index_size,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Ver actividad de autovacuum
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    n_dead_tup AS dead_tuples
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Manualmente hacer VACUUM en tabla pesada
VACUUM ANALYZE tu_tabla;

-- Reindexar tabla (si índices corruptos)
REINDEX TABLE tu_tabla;

-- ============================================
-- 4. IMPORTACIÓN Y EXPORTACIÓN
-- ============================================

-- Importar CSV (desde psql o DBeaver)
\COPY mi_tabla FROM '/ruta/datos.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Exportar a CSV
\COPY (SELECT * FROM mi_tabla WHERE condicion) TO '/ruta/export.csv' WITH (FORMAT csv, HEADER true);

-- Importación masiva deshabilitando constraints (más rápido)
ALTER TABLE mi_tabla DISABLE TRIGGER ALL;
\COPY mi_tabla FROM '/ruta/datos.csv' WITH (FORMAT csv, HEADER true);
ALTER TABLE mi_tabla ENABLE TRIGGER ALL;

-- ============================================
-- 5. ANÁLISIS DE DATOS (EJEMPLOS)
-- ============================================

-- Agregaciones básicas
SELECT 
    region,
    COUNT(*) AS total_ventas,
    SUM(cantidad) AS total_cantidad,
    AVG(precio)::numeric(10,2) AS precio_promedio,
    MAX(precio) AS precio_maximo,
    MIN(precio) AS precio_minimo
FROM ventas_ejemplo
GROUP BY region
ORDER BY total_ventas DESC;

-- Ventas por mes
SELECT 
    DATE_TRUNC('month', fecha) AS mes,
    COUNT(*) AS total_ventas,
    SUM(cantidad * precio)::numeric(15,2) AS ingresos
FROM ventas_ejemplo
GROUP BY mes
ORDER BY mes DESC;

-- Top 10 productos más vendidos
SELECT 
    producto,
    COUNT(*) AS veces_vendido,
    SUM(cantidad) AS unidades_totales,
    SUM(cantidad * precio)::numeric(15,2) AS ingresos_totales
FROM ventas_ejemplo
GROUP BY producto
ORDER BY ingresos_totales DESC
LIMIT 10;

-- Análisis de percentiles
SELECT 
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY precio) AS percentil_25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY precio) AS mediana,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY precio) AS percentil_75,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY precio) AS percentil_95
FROM ventas_ejemplo;

-- Window functions (ranking)
SELECT 
    producto,
    fecha,
    cantidad,
    precio,
    ROW_NUMBER() OVER (PARTITION BY producto ORDER BY precio DESC) AS ranking_precio,
    AVG(precio) OVER (PARTITION BY producto) AS precio_promedio_producto
FROM ventas_ejemplo
LIMIT 100;

-- ============================================
-- 6. ÍNDICES Y PERFORMANCE
-- ============================================

-- Crear índice simple
CREATE INDEX idx_tabla_columna ON mi_tabla(columna);

-- Crear índice compuesto
CREATE INDEX idx_tabla_col1_col2 ON mi_tabla(col1, col2);

-- Crear índice parcial (solo para subset de datos)
CREATE INDEX idx_activos ON mi_tabla(columna) WHERE estado = 'activo';

-- Crear índice B-tree (por defecto, para =, <, >, <=, >=)
CREATE INDEX idx_fecha ON ventas_ejemplo(fecha);

-- Crear índice GIN (para búsqueda de texto completo)
CREATE INDEX idx_texto_gin ON mi_tabla USING GIN(to_tsvector('spanish', columna_texto));

-- Crear índice concurrentemente (no bloquea tabla)
CREATE INDEX CONCURRENTLY idx_grande ON tabla_grande(columna);

-- Ver índices no utilizados (candidatos para eliminar)
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid::regclass)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%pkey'
ORDER BY pg_relation_size(indexrelid::regclass) DESC;

-- ============================================
-- 7. PARTICIONAMIENTO (PARA TABLAS MUY GRANDES)
-- ============================================

-- Crear tabla particionada por fecha
CREATE TABLE ventas_particionada (
    id SERIAL,
    fecha DATE NOT NULL,
    producto VARCHAR(255),
    cantidad INTEGER,
    precio DECIMAL(10,2)
) PARTITION BY RANGE (fecha);

-- Crear particiones por año
CREATE TABLE ventas_2024 PARTITION OF ventas_particionada
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE ventas_2025 PARTITION OF ventas_particionada
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- ============================================
-- 8. USUARIOS Y PERMISOS
-- ============================================

-- Crear usuario de solo lectura
CREATE USER analyst WITH PASSWORD 'secure-password';

-- Dar permisos de solo lectura
GRANT CONNECT ON DATABASE analytics TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst;

-- Ver usuarios conectados
SELECT 
    datname AS database,
    usename AS username,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity
WHERE datname = 'analytics';

-- ============================================
-- 9. BACKUP Y RESTORE
-- ============================================

-- Backup desde terminal (fuera de psql)
-- pg_dump -U postgres -d analytics > backup_$(date +%Y%m%d).sql

-- Backup solo esquema
-- pg_dump -U postgres -d analytics --schema-only > schema.sql

-- Backup solo datos
-- pg_dump -U postgres -d analytics --data-only > data.sql

-- Restore
-- psql -U postgres -d analytics < backup.sql

-- ============================================
-- 10. TIPS DE PERFORMANCE
-- ============================================

-- 1. Siempre usar EXPLAIN ANALYZE antes de queries pesadas
-- 2. Crear índices en columnas de WHERE, JOIN, ORDER BY
-- 3. Evitar SELECT * en tablas grandes
-- 4. Usar LIMIT en queries exploratorias
-- 5. Particionar tablas con >10M de filas
-- 6. Ejecutar VACUUM ANALYZE después de importaciones masivas
-- 7. Usar prepared statements para queries repetidas
-- 8. Considerar materialised views para agregaciones costosas
-- 9. Monitorear pg_stat_statements regularmente
-- 10. Configurar shared_buffers a ~25% de RAM disponible
