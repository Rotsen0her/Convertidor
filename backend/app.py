from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import io
import tempfile
import pandas as pd
from datetime import datetime
from config import Config

# Importar scripts de transformación
from scripts import clientes, venta_material, unir_ventas, exhibidores

app = Flask(__name__)
app.config.from_object(Config)

# Directorio de cache para archivos procesados (filesystem-based para multi-worker)
# Cada usuario tendrá un archivo temporal con metadata JSON
import json
CACHE_DIR = os.path.join(tempfile.gettempdir(), 'convertidor_cache')
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, mode=0o755)

ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

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

def save_to_cache(user_id, filename, file_path):
    """Guarda un archivo procesado en el cache del usuario (filesystem) - copia directa sin modificar"""
    # Leer el archivo como bytes sin procesar
    with open(file_path, 'rb') as f:
        csv_data = f.read()
    
    if len(csv_data) == 0:
        print(f"[WARNING] Intentando guardar archivo vacío!")
    
    # Guardar archivo CSV en filesystem
    cache_file_path = os.path.join(CACHE_DIR, f'user_{user_id}.csv')
    cache_meta_path = os.path.join(CACHE_DIR, f'user_{user_id}.json')
    
    with open(cache_file_path, 'wb') as f:
        f.write(csv_data)
    
    # Guardar metadata
    metadata = {
        'filename': filename,
        'timestamp': datetime.now().isoformat(),
        'size': len(csv_data)
    }
    with open(cache_meta_path, 'w') as f:
        json.dump(metadata, f)
    
    print(f"[INFO] Archivo guardado en cache: {filename} ({len(csv_data)} bytes)")
    
def get_from_cache(user_id):
    """Obtiene archivo del cache del usuario (filesystem)"""
    cache_file_path = os.path.join(CACHE_DIR, f'user_{user_id}.csv')
    cache_meta_path = os.path.join(CACHE_DIR, f'user_{user_id}.json')
    
    if not os.path.exists(cache_file_path) or not os.path.exists(cache_meta_path):
        return None
    
    try:
        with open(cache_file_path, 'rb') as f:
            data = f.read()
        
        with open(cache_meta_path, 'r') as f:
            metadata = json.load(f)
        
        return {
            'filename': metadata['filename'],
            'data': data,
            'timestamp': datetime.fromisoformat(metadata['timestamp'])
        }
    except Exception as e:
        print(f"[ERROR] Error reading cache for user {user_id}: {e}")
        return None

# RUTAS DE AUTENTICACIÓN
@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico', mimetype='image/x-icon')

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

# PROCESAMIENTO DE ARCHIVOS (en memoria)
@app.route('/procesar/<tipo>', methods=['POST'])
@login_required
def procesar_archivo(tipo):
    try:
        user_id = session.get('user_id')
        
        # Para unión de ventas (2 archivos)
        if tipo == 'union_ventas':
            if 'archivo_acum' not in request.files or 'archivo_mes' not in request.files:
                return jsonify({'success': False, 'error': 'Faltan archivos'}), 400
            
            file_acum = request.files['archivo_acum']
            file_mes = request.files['archivo_mes']
            
            if file_acum.filename == '' or file_mes.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionaron archivos'}), 400
            
            if not (allowed_file(file_acum.filename) and allowed_file(file_mes.filename)):
                return jsonify({'success': False, 'error': 'Tipo de archivo no válido'}), 400
            
            try:
                # Guardar archivos temporalmente para procesarlos con el script
                temp_dir = tempfile.mkdtemp()
                temp_acum = os.path.join(temp_dir, secure_filename(file_acum.filename))
                temp_mes = os.path.join(temp_dir, secure_filename(file_mes.filename))
                
                file_acum.save(temp_acum)
                file_mes.save(temp_mes)
                
                # Procesar con el script de unir_ventas
                print(f"[INFO] Procesando unión de ventas usando script")
                unir_ventas.ejecutar(temp_acum, temp_mes, carpeta_salida=temp_dir)
                
                # Ruta al resultado
                resultado_path = os.path.join(temp_dir, 'ventas_acum.csv')
                
                if not os.path.exists(resultado_path):
                    return jsonify({'success': False, 'error': 'El archivo procesado no se generó correctamente'}), 500
                
                # Guardar en cache (copia directa del archivo sin modificar)
                save_to_cache(user_id, 'ventas_acum.csv', resultado_path)
                
                # Limpiar archivos temporales
                import shutil
                shutil.rmtree(temp_dir)
                
                return jsonify({
                    'success': True, 
                    'message': 'Archivos unidos correctamente',
                    'download_url': url_for('download_file')
                })
                
            except ValueError as e:
                return jsonify({'success': False, 'error': f'Error al leer archivos: {str(e)}'}), 400
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': f'Error al procesar: {str(e)}'}), 500
        
        # Para archivos individuales
        if 'archivo' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['archivo']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó ningún archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Tipo de archivo no válido. Solo se permiten: xlsx, xls, csv'}), 400
        
        try:
            print(f"[INFO] Procesando archivo {file.filename} tipo '{tipo}' para user_id: {user_id}")
            
            # Guardar archivo temporal para procesarlo con los scripts
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(temp_file)
            
            # Procesar según el tipo usando los scripts
            if tipo == 'clientes':
                print(f"[INFO] Procesando maestra de clientes usando script")
                clientes.ejecutar(temp_file, carpeta_salida=temp_dir)
                output_filename = 'maestra_clientes.csv'
                
            elif tipo == 'venta_material':
                mes = request.form.get('mes', '')
                print(f"[INFO] Procesando venta_material con mes: {mes} usando script")
                venta_material.ejecutar(temp_file, mes, carpeta_salida=temp_dir)
                output_filename = 'ventas_mes.csv'
            
            elif tipo == 'exhibidores':
                print(f"[INFO] Procesando exhibidores usando script")
                exhibidores.ejecutar(temp_file, carpeta_salida=temp_dir)
                output_filename = 'Exhibidores.csv'
            
            else:
                return jsonify({'success': False, 'error': f'Tipo de procesamiento "{tipo}" no reconocido'}), 400
            
            # Ruta al archivo procesado
            resultado_path = os.path.join(temp_dir, output_filename)
            
            if not os.path.exists(resultado_path):
                return jsonify({'success': False, 'error': 'El archivo procesado no se generó correctamente'}), 500
            
            print(f"[INFO] Guardando en cache: {output_filename}")
            # Guardar en cache (copia directa del archivo sin modificar)
            save_to_cache(user_id, output_filename, resultado_path)
            
            # Limpiar archivos temporales
            import shutil
            if os.path.exists(temp_file):
                shutil.rmtree(os.path.dirname(temp_file), ignore_errors=True)
            
            return jsonify({
                'success': True, 
                'message': 'Archivo procesado correctamente',
                'download_url': url_for('download_file')
            })
                
        except ValueError as e:
            print(f"[ERROR] ValueError: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Error al leer archivo: {str(e)}'}), 400
        except Exception as e:
            print(f"[ERROR] Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Error al procesar archivo: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error general: {str(e)}'}), 500

# API para archivos recientes (desde cache)
@app.route('/api/recent-files')
@login_required
def api_recent_files():
    try:
        user_id = session.get('user_id')
        cached_file = get_from_cache(user_id)
        
        archivos = []
        if cached_file:
            archivos.append({
                'nombre': cached_file['filename'],
                'tamano': len(cached_file['data']),
                'fecha': cached_file['timestamp'].timestamp()
            })
        
        return jsonify({'success': True, 'archivos': archivos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Ruta de descarga (desde cache)
@app.route('/download/')
@login_required
def download_file():
    """Descarga el archivo transformado del cache del usuario"""
    try:
        user_id = session.get('user_id')
        cached_file = get_from_cache(user_id)
        
        if not cached_file:
            return jsonify({'success': False, 'error': 'No hay archivo disponible para descargar'}), 404
        
        # Crear respuesta con el archivo en memoria
        return send_file(
            io.BytesIO(cached_file['data']),
            mimetype='text/csv',
            as_attachment=True,
            download_name=cached_file['filename']
        )
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al descargar: {str(e)}'}), 500

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
    return procesar_archivo('exhibidores')

if __name__ == '__main__':
    app.run(debug=True)
