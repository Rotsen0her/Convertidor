# 📋 Instalación de MySQL en Windows

## Opción 1: Instalar MySQL Server (Método Oficial)

### 1. Descargar MySQL
1. Ir a: https://dev.mysql.com/downloads/installer/
2. Descargar: **MySQL Installer for Windows** (mysql-installer-web-community)
3. Ejecutar el instalador

### 2. Durante la instalación:
- Seleccionar: **Developer Default** o **Server only**
- En "Type and Networking":
  - Port: **3306** (por defecto)
  - Configurar firewall si es necesario
- En "Authentication Method":
  - Usar: **Use Strong Password Encryption**
- Configurar contraseña de root (déjala en blanco para desarrollo o usa una simple)
- Completar instalación

### 3. Verificar instalación
```powershell
# En PowerShell:
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
.\mysql.exe --version
```

### 4. Agregar MySQL al PATH (Opcional pero recomendado)
1. Buscar "Variables de entorno" en Windows
2. En "Variables del sistema" buscar "Path"
3. Agregar: `C:\Program Files\MySQL\MySQL Server 8.0\bin`

---

## Opción 2: Instalar XAMPP (Más Fácil - Recomendado para Principiantes)

### 1. Descargar XAMPP
- Ir a: https://www.apachefriends.org/download.html
- Descargar versión para Windows
- Ejecutar instalador

### 2. Durante instalación:
- Marcar: **MySQL** y **phpMyAdmin**
- Instalar en: `C:\xampp`

### 3. Iniciar MySQL
- Abrir **XAMPP Control Panel**
- Hacer clic en **Start** al lado de MySQL

### 4. Configurar en tu aplicación
Editar el archivo `.env`:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=zafiro_bi
```

---

## Opción 3: Usar SQLite (Alternativa sin instalación)

Si prefieres no instalar MySQL, puedes usar SQLite que no requiere servidor.

### Ventajas:
- ✅ No requiere instalación de servidor
- ✅ Base de datos en un archivo
- ✅ Perfecto para desarrollo

### Desventajas:
- ❌ No es MySQL (tendrías que migrar después)
- ❌ Menos características que MySQL

---

## 🚀 Después de Instalar MySQL

### 1. Crear la base de datos
```powershell
# Abrir PowerShell
cd "C:\Users\andre\OneDrive\Documentos\Proyectos-GitHub\Convertidor"
python init_db.py
```

### 2. Iniciar la aplicación
```powershell
python app.py
```

### 3. Abrir en navegador
http://localhost:5000

### 4. Login
- Usuario: **admin**
- Contraseña: **admin123**

---

## ⚠️ Problemas Comunes

### MySQL no inicia en XAMPP
1. Verificar que el puerto 3306 no esté en uso
2. Ejecutar XAMPP como Administrador
3. Revisar logs en: `C:\xampp\mysql\data\mysql_error.log`

### Error: Access denied
- Verificar usuario y contraseña en `.env`
- Probar sin contraseña (dejar vacío): `MYSQL_PASSWORD=`

### Error: Database does not exist
- Ejecutar: `python init_db.py`
- O crear manualmente en phpMyAdmin

---

## 📞 ¿Qué Opción Elegir?

### Para Principiantes: **XAMPP** 🏆
- Fácil de instalar y usar
- Incluye phpMyAdmin (interfaz gráfica)
- Un solo instalador para todo

### Para Desarrolladores: **MySQL Server**
- Instalación oficial
- Mejor rendimiento
- Más control

### Para Pruebas Rápidas: **SQLite**
- Sin instalación
- Rápido de configurar
- Ideal para prototipos
