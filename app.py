from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de archivos (compatibilidad)
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
TRANSFORMED_FOLDER = app.config['TRANSFORMED_FOLDER']
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSFORMED_FOLDER, exist_ok=True)

mysql = MySQL(app)

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para continuar', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir rol admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para continuar', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# RUTAS DE AUTENTICACIÓN
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, usuario, password, rol FROM usuarios WHERE usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['usuario'] = user[1]
            session['rol'] = user[3]
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

# RUTAS PRINCIPALES
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

# GESTIÓN DE USUARIOS (SOLO ADMIN)
@app.route('/usuarios')
@admin_required
def usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, usuario, rol FROM usuarios ORDER BY id DESC")
    users = cur.fetchall()
    cur.close()
    return render_template('usuarios.html', usuarios=users)

@app.route('/usuarios/crear', methods=['POST'])
@admin_required
def crear_usuario():
    usuario = request.form['usuario']
    password = request.form['password']
    rol = request.form['rol']
    
    hashed_password = generate_password_hash(password)
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (%s, %s, %s)", 
                   (usuario, hashed_password, rol))
        mysql.connection.commit()
        cur.close()
        flash('Usuario creado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al crear usuario: {str(e)}', 'danger')
    
    return redirect(url_for('usuarios'))

@app.route('/usuarios/eliminar/<int:id>')
@admin_required
def eliminar_usuario(id):
    if id == session.get('user_id'):
        flash('No puedes eliminar tu propio usuario', 'warning')
        return redirect(url_for('usuarios'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Usuario eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar usuario: {str(e)}', 'danger')
    
    return redirect(url_for('usuarios'))

# API ENDPOINTS PARA USUARIOS
@app.route('/api/usuarios', methods=['GET'])
@admin_required
def api_get_usuarios():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, usuario, rol FROM usuarios ORDER BY id DESC")
        users = cur.fetchall()
        cur.close()
        
        usuarios_list = []
        for user in users:
            usuarios_list.append({
                'id': user[0],
                'usuario': user[1],
                'rol': user[2]
            })
        
        return jsonify({'success': True, 'usuarios': usuarios_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/usuarios', methods=['POST'])
@admin_required
def api_crear_usuario():
    try:
        data = request.get_json()
        usuario = data.get('usuario')
        password = data.get('password')
        rol = data.get('rol', 'usuario')
        
        if not usuario or not password:
            return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400
        
        hashed_password = generate_password_hash(password)
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (%s, %s, %s)", 
                   (usuario, hashed_password, rol))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
@admin_required
def api_eliminar_usuario(id):
    try:
        if id == session.get('user_id'):
            return jsonify({'success': False, 'error': 'No puedes eliminar tu propio usuario'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Usuario eliminado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/usuarios/<int:id>', methods=['PUT'])
@admin_required
def api_actualizar_usuario(id):
    try:
        data = request.get_json()
        usuario = data.get('usuario')
        password = data.get('password')
        rol = data.get('rol')
        
        if not usuario or not rol:
            return jsonify({'success': False, 'error': 'Usuario y rol son requeridos'}), 400
        
        cur = mysql.connection.cursor()
        
        # Si se proporcionó una nueva contraseña
        if password and password.strip():
            hashed_password = generate_password_hash(password)
            cur.execute("UPDATE usuarios SET usuario = %s, password = %s, rol = %s WHERE id = %s", 
                       (usuario, hashed_password, rol, id))
        else:
            # Solo actualizar usuario y rol
            cur.execute("UPDATE usuarios SET usuario = %s, rol = %s WHERE id = %s", 
                       (usuario, rol, id))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Usuario actualizado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# PROCESAMIENTO DE ARCHIVOS
@app.route('/procesar/<tipo>', methods=['POST'])
@login_required
def procesar_archivo(tipo):
    try:
        # Para unión de ventas (2 archivos)
        if tipo == 'union_ventas':
            if 'archivo_acum' not in request.files or 'archivo_mes' not in request.files:
                return jsonify({'success': False, 'error': 'Faltan archivos'}), 400
            
            file_acum = request.files['archivo_acum']
            file_mes = request.files['archivo_mes']
            
            if file_acum.filename == '' or file_mes.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionaron archivos'}), 400
            
            if allowed_file(file_acum.filename) and allowed_file(file_mes.filename):
                filename_acum = secure_filename(file_acum.filename)
                filename_mes = secure_filename(file_mes.filename)
                
                filepath_acum = os.path.join(app.config['UPLOAD_FOLDER'], filename_acum)
                filepath_mes = os.path.join(app.config['UPLOAD_FOLDER'], filename_mes)
                
                file_acum.save(filepath_acum)
                file_mes.save(filepath_mes)
                
                try:
                    # Importar y ejecutar script
                    import scripts.unir_ventas as unir_ventas
                    unir_ventas.ejecutar(filepath_acum, filepath_mes, TRANSFORMED_FOLDER)
                    return jsonify({
                        'success': True, 
                        'message': 'Archivos unidos correctamente',
                        'download_url': url_for('download_file', filename='ventas_acum.csv')
                    })
                except ImportError:
                    return jsonify({'success': False, 'error': 'Script de unión de ventas no encontrado'}), 404
                except ValueError as e:
                    # Error de formato de archivo
                    error_msg = str(e)
                    if 'Expected BOF record' in error_msg or 'Unsupported format' in error_msg:
                        return jsonify({'success': False, 'error': 'Uno de los archivos .xls parece estar corrupto o es en realidad un archivo HTML. Por favor, abre los archivos en Excel y guárdalos como .xlsx'}), 400
                    return jsonify({'success': False, 'error': f'Error de formato: {error_msg}'}), 400
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Error al procesar: {str(e)}'}), 500
            
            return jsonify({'success': False, 'error': 'Tipo de archivo no válido'}), 400
        
        # Para archivos individuales
        if 'archivo' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['archivo']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Ejecutar según el tipo
            try:
                if tipo == 'clientes':
                    import scripts.clientes as clientes
                    clientes.ejecutar(filepath, TRANSFORMED_FOLDER)
                    return jsonify({
                        'success': True, 
                        'message': 'Archivo de clientes procesado correctamente',
                        'download_url': url_for('download_file', filename='maestra_clientes.csv')
                    })
                    
                elif tipo == 'venta_material':
                    mes = request.form.get('mes', '')
                    import scripts.venta_material as venta_material
                    venta_material.ejecutar(filepath, mes, TRANSFORMED_FOLDER)
                    filename = f'venta_material_{mes}.csv' if mes else 'venta_material.csv'
                    return jsonify({
                        'success': True, 
                        'message': f'Archivo de venta por material procesado correctamente',
                        'download_url': url_for('download_file', filename=filename)
                    })
                
                else:
                    return jsonify({'success': False, 'error': f'Tipo de procesamiento "{tipo}" no reconocido'}), 400
                    
            except ImportError as e:
                return jsonify({'success': False, 'error': f'Script de procesamiento no encontrado: {str(e)}'}), 404
            except ValueError as e:
                # Error de formato de archivo
                error_msg = str(e)
                if 'Expected BOF record' in error_msg or 'Unsupported format' in error_msg:
                    return jsonify({'success': False, 'error': 'El archivo .xls parece estar corrupto o es en realidad un archivo HTML. Por favor, abre el archivo en Excel y guárdalo como .xlsx'}), 400
                return jsonify({'success': False, 'error': f'Error de formato: {error_msg}'}), 400
            except Exception as e:
                return jsonify({'success': False, 'error': f'Error al procesar archivo: {str(e)}'}), 500
        
        return jsonify({'success': False, 'error': 'Tipo de archivo no válido. Solo se permiten: xlsx, xls, csv'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error general: {str(e)}'}), 500

@app.route('/archivos-procesados')
@login_required
def archivos_procesados():
    archivos = []
    if os.path.exists(TRANSFORMED_FOLDER):
        for filename in os.listdir(TRANSFORMED_FOLDER):
            if filename.endswith(('.csv', '.xlsx', '.xls')):
                filepath = os.path.join(TRANSFORMED_FOLDER, filename)
                archivos.append({
                    'nombre': filename,
                    'tamano': os.path.getsize(filepath),
                    'fecha': os.path.getmtime(filepath)
                })
    return jsonify(archivos)

# API para archivos recientes
@app.route('/api/recent-files')
@login_required
def api_recent_files():
    try:
        archivos = []
        if os.path.exists(TRANSFORMED_FOLDER):
            for filename in os.listdir(TRANSFORMED_FOLDER):
                if filename.endswith(('.csv', '.xlsx', '.xls')):
                    filepath = os.path.join(TRANSFORMED_FOLDER, filename)
                    archivos.append({
                        'nombre': filename,
                        'tamano': os.path.getsize(filepath),
                        'fecha': os.path.getmtime(filepath)
                    })
        
        # Ordenar por fecha (más recientes primero)
        archivos.sort(key=lambda x: x['fecha'], reverse=True)
        
        return jsonify({'success': True, 'archivos': archivos[:10]})  # Últimos 10
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta de descarga
@app.route('/download/<filename>')
@login_required
def download_file(filename):
    """Permite descargar archivos transformados"""
    try:
        return send_from_directory(TRANSFORMED_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Archivo no encontrado: {str(e)}'}), 404

# Rutas de transformación simplificadas
@app.route('/transform/clientes', methods=['POST'])
@login_required
def transform_clientes():
    return procesar_archivo('clientes')

@app.route('/transform/ventas', methods=['POST'])
@login_required
def transform_ventas():
    return procesar_archivo('venta_material')

@app.route('/transform/union', methods=['POST'])
@login_required
def transform_union():
    return procesar_archivo('union_ventas')

@app.route('/transform/exhibidores', methods=['POST'])
@login_required
def transform_exhibidores():
    # Por ahora usa el mismo script de clientes
    # Puedes crear un script específico después
    return procesar_archivo('clientes')

if __name__ == '__main__':
    app.run(debug=True)