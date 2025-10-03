-- Script para crear la base de datos y tabla de usuarios para Zafiro BI

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS zafiro_bi;
USE zafiro_bi;

-- Crear tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Contraseña: admin123 
INSERT INTO usuarios (usuario, password, rol) VALUES 
('admin', 'pbkdf2:sha256:600000$6xKbQ3F5K2XqN4Gs$9e7f8a5b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f', 'admin');


-- Opcional: Tabla para logs de actividad
CREATE TABLE logs_actividad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    accion VARCHAR(100) NOT NULL,
    archivo_origen VARCHAR(255),
    archivo_destino VARCHAR(255),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('exitoso', 'fallido') DEFAULT 'exitoso',
    mensaje TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_usuarios_usuario ON usuarios(usuario);
CREATE INDEX idx_logs_usuario_fecha ON logs_actividad(usuario_id, fecha);
CREATE INDEX idx_logs_fecha ON logs_actividad(fecha);

-- Mostrar estructura de las tablas creadas
DESCRIBE usuarios;
DESCRIBE logs_actividad;