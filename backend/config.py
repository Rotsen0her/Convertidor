# Configuración de la aplicación Flask

import os
from dotenv import load_dotenv
import secrets

load_dotenv()

class Config:
    # Generar una clave secreta nueva cada vez que se inicia el servidor
    # Esto invalida las sesiones anteriores automáticamente
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Configurar la sesión para que expire al cerrar el navegador
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora en segundos
    
    # Configuración MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'db'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DATABASE') or 'joseberrio_db'
    
    # Configuración de archivos
    UPLOAD_FOLDER = 'uploads'
    TRANSFORMED_FOLDER = 'transformados'
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1GB max (aumentado para archivos acumulados grandes)
    
    # Extensiones permitidas
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}