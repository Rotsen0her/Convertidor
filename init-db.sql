-- Script de inicialización de base de datos
-- Crea la base de datos y las tablas necesarias

CREATE DATABASE IF NOT EXISTS convertidor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE convertidor_db;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'usuario') DEFAULT 'usuario',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Usuario admin por defecto (password: admin123)
-- IMPORTANTE: Cambiar esta contraseña después del primer login
INSERT INTO usuarios (usuario, password, rol) VALUES
('admin', 'scrypt:32768:8:1$yZQH8Jf0rGJ4Rwzm$8a8f5d8e7a0b2c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7', 'admin')
ON DUPLICATE KEY UPDATE id=id;

-- Crear índices para optimizar búsquedas
CREATE INDEX idx_usuario ON usuarios(usuario);
CREATE INDEX idx_rol ON usuarios(rol);
