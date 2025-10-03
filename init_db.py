"""
Script para crear un usuario admin por defecto en la base de datos
"""
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
import MySQLdb

load_dotenv()

# Configuración de la base de datos
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'zafiro_bi')

print("🔧 Conectando a la base de datos...")
print(f"   Host: {MYSQL_HOST}:{MYSQL_PORT}")
print(f"   Usuario: {MYSQL_USER}")
print(f"   Base de datos: {MYSQL_DB}")
print(f"   Contraseña: {'*' * len(MYSQL_PASSWORD) if MYSQL_PASSWORD else '(vacía)'}")

try:
    # Conectar a MySQL sin especificar base de datos
    print("\n🔌 Conectando a MySQL...")
    conn = MySQLdb.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD
    )
    cursor = conn.cursor()
    
    print("✅ Conexión exitosa\n")
    
    # Crear base de datos si no existe
    print(f"📦 Creando base de datos '{MYSQL_DB}' si no existe...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
    cursor.execute(f"USE {MYSQL_DB}")
    conn.commit()
    print(f"✅ Base de datos '{MYSQL_DB}' lista\n")
    
    # Crear tabla si no existe
    print("📋 Creando tabla usuarios si no existe...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            rol ENUM('admin', 'usuario') DEFAULT 'usuario',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("✅ Tabla usuarios lista\n")
    
    # Verificar si ya existe el usuario admin
    cursor.execute("SELECT id FROM usuarios WHERE usuario = 'admin'")
    admin_exists = cursor.fetchone()
    
    if admin_exists:
        print("⚠️  El usuario 'admin' ya existe")
        print("   ID:", admin_exists[0])
    else:
        # Crear usuario admin
        print("👤 Creando usuario admin...")
        password = 'admin123'
        hashed_password = generate_password_hash(password)
        
        cursor.execute(
            "INSERT INTO usuarios (usuario, password, rol) VALUES (%s, %s, %s)",
            ('admin', hashed_password, 'admin')
        )
        conn.commit()
        
        print("✅ Usuario admin creado exitosamente")
        print(f"   Usuario: admin")
        print(f"   Contraseña: {password}")
        print("   ⚠️  IMPORTANTE: Cambia esta contraseña después del primer login\n")
    
    # Mostrar todos los usuarios
    cursor.execute("SELECT id, usuario, rol FROM usuarios")
    usuarios = cursor.fetchall()
    
    print("📊 Usuarios en la base de datos:")
    print("=" * 50)
    for user in usuarios:
        print(f"   ID: {user[0]} | Usuario: {user[1]} | Rol: {user[2]}")
    print("=" * 50)
    
    cursor.close()
    conn.close()
    print("\n✅ Script completado exitosamente")
    
except MySQLdb.Error as e:
    print(f"\n❌ Error de MySQL: {e}")
    print("\n💡 Verifica que:")
    print("   1. MySQL esté corriendo")
    print("   2. Las credenciales en .env sean correctas")
    print("   3. La base de datos exista")
    print("   4. El usuario tenga permisos")
except Exception as e:
    print(f"\n❌ Error: {e}")
