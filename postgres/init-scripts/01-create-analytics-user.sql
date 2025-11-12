-- Script de inicialización para PostgreSQL Analytics
-- Se ejecuta automáticamente al crear el contenedor por primera vez

-- Extensiones útiles para análisis de datos
CREATE EXTENSION IF NOT EXISTS pg_stat_statements; -- Estadísticas de queries
CREATE EXTENSION IF NOT EXISTS pg_trgm;           -- Búsqueda fuzzy
CREATE EXTENSION IF NOT EXISTS btree_gin;         -- Índices optimizados
CREATE EXTENSION IF NOT EXISTS btree_gist;        -- Índices optimizados

-- Opcional: Crear usuario de solo lectura para analistas
-- Descomenta las siguientes líneas si necesitas un usuario con acceso limitado
-- CREATE USER analyst WITH PASSWORD 'change-this-password';
-- GRANT CONNECT ON DATABASE analytics TO analyst;
-- GRANT USAGE ON SCHEMA public TO analyst;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst;

COMMENT ON DATABASE analytics IS 'Base de datos para análisis de datos - 1M+ registros';
