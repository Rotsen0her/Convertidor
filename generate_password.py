#!/usr/bin/env python3
"""
Script para generar hash de contraseña para usuarios de Convertidor
Uso: python generate_password.py
"""

from werkzeug.security import generate_password_hash
import sys

def main():
    print("=" * 50)
    print("Generador de Contraseñas Hash - Convertidor")
    print("=" * 50)
    print()
    
    # Solicitar contraseña
    password = input("Ingresa la contraseña a hashear: ").strip()
    
    if not password:
        print("❌ Error: La contraseña no puede estar vacía")
        sys.exit(1)
    
    if len(password) < 8:
        print("⚠️  Advertencia: Se recomienda usar contraseñas de al menos 8 caracteres")
    
    # Generar hash
    hashed = generate_password_hash(password)
    
    print()
    print("✅ Hash generado:")
    print("-" * 50)
    print(hashed)
    print("-" * 50)
    print()
    print("📋 Para actualizar en la base de datos, ejecuta:")
    print()
    print(f"UPDATE usuarios SET password = '{hashed}' WHERE usuario = 'admin';")
    print()

if __name__ == "__main__":
    main()
