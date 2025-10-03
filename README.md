# Zafiro BI - Transformador de Datos

Una aplicación web desarrollada con Flask y Tailwind CSS para transformar archivos de datos de ECOM.

## Características

- 🔐 **Sistema de autenticación** con roles de usuario y administrador
- 📊 **Transformación de archivos** Excel/CSV con diferentes tipos de procesamientos
- 👥 **Gestión de usuarios** (solo para administradores)
- 📁 **Carga y descarga** de archivos con drag & drop
- 🎨 **Interfaz moderna** con Tailwind CSS
- 📱 **Diseño responsivo** para diferentes dispositivos

## Tipos de Transformación Soportados

1. **Base de datos de clientes** - Procesa la maestra de clientes de ECOM
2. **Informe Venta x Material x Cliente** - Procesa informes de ventas con filtro por mes
3. **Unión ventas mes y anuales** - Combina archivos de ventas mensuales y acumuladas
4. **Base de datos exhibidores** - Procesa la maestra de exhibidores

## Requisitos

- Python 3.8+
- MySQL 5.7+
- Node.js (para Tailwind CSS)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Convertidor
```

### 2. Crear entorno virtual

```bash
python -m venv venv
venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En Linux/Mac
```

### 3. Instalar dependencias de Python

```bash
pip install flask flask-mysqldb werkzeug pandas openpyxl xlrd python-dotenv
```

### 4. Configurar base de datos MySQL

1. Asegúrate de que MySQL esté ejecutándose
2. Ejecuta el script SQL para crear la base de datos:

```bash
mysql -u root -p < database_setup.sql
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_password_mysql
MYSQL_DB=zafiro_bi
```

### 6. Instalar y configurar Tailwind CSS

```bash
npm install
npm run build-css
```

### 7. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Uso

### Primer acceso

- **Usuario:** admin
- **Contraseña:** admin123

⚠️ **Importante:** Cambia la contraseña del administrador después del primer acceso.

### Crear nuevos usuarios (Solo Admin)

1. Accede con cuenta de administrador
2. Ve a "Gestión de Usuarios" en el menú
3. Haz clic en "Nuevo Usuario"
4. Completa el formulario con los datos del usuario

### Transformar archivos

1. Selecciona el tipo de transformación en el panel izquierdo
2. Arrastra el archivo o haz clic para seleccionarlo
3. Completa los campos adicionales si son requeridos (ej: mes para ventas)
4. Haz clic en "Procesar"
5. Descarga el archivo transformado cuando esté listo

## Estructura del Proyecto

```
Convertidor/
├── app.py                 # Aplicación principal Flask
├── config.py             # Configuraciones
├── database_setup.sql    # Script para crear la BD
├── package.json          # Dependencias de Node.js
├── tailwind.config.js    # Configuración de Tailwind
├── static/
│   └── css/
│       └── output.css    # CSS compilado de Tailwind
├── templates/
│   ├── base.html         # Template base
│   ├── login.html        # Página de login
│   ├── index.html        # Dashboard principal
│   └── usuarios_new.html # Gestión de usuarios
├── uploads/              # Archivos subidos (temporal)
└── transformados/        # Archivos procesados
```

## Scripts de Transformación

Los scripts de transformación están integrados en el archivo `app.py` en las funciones:

- `transform_clientes_file()` - Para archivos de clientes
- `transform_ventas_file()` - Para archivos de ventas
- `transform_union_file()` - Para unión de archivos
- `transform_exhibidores_file()` - Para archivos de exhibidores

## Seguridad

- Todas las rutas están protegidas con autenticación
- Solo administradores pueden gestionar usuarios
- Contraseñas hasheadas con werkzeug.security
- Validación de tipos de archivo permitidos
- Protección contra ataques de subida de archivos

## API Endpoints

### Autenticación
- `POST /login` - Iniciar sesión
- `GET /logout` - Cerrar sesión

### Gestión de usuarios (Solo Admin)
- `GET /api/usuarios` - Listar usuarios
- `POST /api/usuarios` - Crear usuario
- `PUT /api/usuarios/<id>` - Actualizar usuario
- `DELETE /api/usuarios/<id>` - Eliminar usuario

### Transformación de archivos
- `POST /transform/clientes` - Transformar clientes
- `POST /transform/ventas` - Transformar ventas
- `POST /transform/union` - Unir archivos
- `POST /transform/exhibidores` - Transformar exhibidores

### Archivos
- `GET /api/recent-files` - Archivos recientes
- `GET /download/<filename>` - Descargar archivo

## Desarrollo

### Recompilar Tailwind CSS

```bash
npm run watch-css  # Modo watch para desarrollo
npm run build-css  # Build para producción
```

### Estructura de la Base de Datos

```sql
usuarios (
    id, usuario, password, rol, created_at, updated_at
)

logs_actividad (
    id, usuario_id, accion, archivo_origen, 
    archivo_destino, fecha, estado, mensaje
)
```

## Solución de Problemas

### Error de conexión a MySQL
- Verifica que MySQL esté ejecutándose
- Confirma las credenciales en el archivo `.env`
- Asegúrate de que la base de datos `zafiro_bi` exista

### Error al cargar archivos
- Verifica que las carpetas `uploads` y `transformados` existan
- Confirma que los archivos sean .xlsx, .xls o .csv
- Verifica que el archivo no exceda 16MB

### Error en Tailwind CSS
- Ejecuta `npm install` para instalar dependencias
- Ejecuta `npm run build-css` para compilar los estilos

## Licencia

Este proyecto es propiedad de Mercantil Zafiro SAS.

## Soporte

Para soporte técnico, contacta al equipo de desarrollo.