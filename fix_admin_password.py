"""Script para actualizar la contraseña del usuario admin"""
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import os
import MySQLdb

load_dotenv()

try:
    # Generar el hash correcto
    password = 'admin123'
    hashed = generate_password_hash(password)
    
    print(f"🔐 Hash generado para '{password}':")
    print(f"   {hashed}\n")
    
    # Conectar a la base de datos
    conn = MySQLdb.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        passwd=os.getenv('MYSQL_PASSWORD', ''),
        db=os.getenv('MYSQL_DB', 'zafiro_bi')
    )
    
    cursor = conn.cursor()
    
    # Actualizar la contraseña del admin
    cursor.execute("UPDATE usuarios SET password = %s WHERE usuario = 'admin'", (hashed,))
    conn.commit()
    
    print("✅ Contraseña del usuario 'admin' actualizada exitosamente")
    print(f"   Usuario: admin")
    print(f"   Contraseña: {password}")
    
    # Verificar
    cursor.execute("SELECT id, usuario, rol FROM usuarios WHERE usuario = 'admin'")
    admin = cursor.fetchone()
    
    if admin:
        print(f"\n📊 Usuario admin verificado:")
        print(f"   ID: {admin[0]}")
        print(f"   Usuario: {admin[1]}")
        print(f"   Rol: {admin[2]}")
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
