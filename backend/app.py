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

def is_html_file(file_content):
    """Detecta si un archivo es realmente HTML disfrazado"""
    # Lee los primeros 512 bytes para detectar HTML
    header = file_content[:512].decode('latin-1', errors='ignore').lower()
    return '<html' in header or '<!doctype html' in header or '<htm' in header

def clean_dataframe(df):
    """Limpia un DataFrame eliminando filas vacías, duplicados y headers repetidos"""
    print(f"[INFO] Limpiando DataFrame: {len(df)} filas iniciales, {len(df.columns)} columnas iniciales")
    
    if len(df) == 0:
        print(f"[WARNING] DataFrame vacío, retornando sin cambios")
        return df
    
    # 1. Eliminar columnas completamente sin nombre o Unnamed
    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
    if unnamed_cols:
        print(f"[INFO] Eliminando {len(unnamed_cols)} columnas sin nombre")
        df = df.drop(columns=unnamed_cols)
    
    # 2. Eliminar columnas completamente vacías
    initial_cols = len(df.columns)
    df = df.dropna(axis=1, how='all')
    if len(df.columns) < initial_cols:
        print(f"[INFO] Eliminadas {initial_cols - len(df.columns)} columnas completamente vacías")
    
    # 3. Eliminar filas completamente vacías
    initial_rows = len(df)
    df = df.dropna(axis=0, how='all')
    if len(df) < initial_rows:
        print(f"[INFO] Eliminadas {initial_rows - len(df)} filas completamente vacías")
    
    if len(df) == 0:
        print(f"[WARNING] DataFrame quedó vacío después de eliminar filas/columnas vacías")
        return df
    
    # 4. Buscar la última fila con datos reales
    last_valid = df.last_valid_index()
    if last_valid is not None and last_valid < len(df) - 1:
        rows_trimmed = len(df) - last_valid - 1
        df = df.loc[:last_valid]
        print(f"[INFO] Recortadas {rows_trimmed} filas vacías al final")
    
    # 5. Eliminar SOLO la primera fila SI es exactamente igual a los headers
    # (No revisar todas las filas, solo la primera)
    if len(df) > 0:
        headers = df.columns.astype(str).tolist()
        first_row = df.iloc[0].astype(str).tolist()
        
        if first_row == headers:
            print(f"[INFO] Primera fila es header duplicado, eliminando")
            df = df.iloc[1:].reset_index(drop=True)
    

    # 7. Resetear índice
    df = df.reset_index(drop=True)
    
    # 8. Limpiar caracteres mal codificados comunes (UTF-8 mal interpretado como Latin-1)
    print(f"[INFO] Limpiando caracteres mal codificados...")
    for col in df.columns:
        if df[col].dtype == 'object':  # Solo columnas de texto
            df[col] = df[col].astype(str).str.replace('Ã', 'A', regex=False)
            df[col] = df[col].str.replace('Ã', 'O', regex=False)
            df[col] = df[col].str.replace('Ã', 'I', regex=False)
            df[col] = df[col].str.replace('Ã±', 'ñ', regex=False)
            df[col] = df[col].str.replace('Ã³', 'ó', regex=False)
            df[col] = df[col].str.replace('Ã­', 'í', regex=False)
            df[col] = df[col].str.replace('Ã¡', 'á', regex=False)
            df[col] = df[col].str.replace('Ã©', 'é', regex=False)
            df[col] = df[col].str.replace('Ãº', 'ú', regex=False)
            df[col] = df[col].str.replace('Ã', 'Ñ', regex=False)
            df[col] = df[col].str.replace('Ã"', 'Ó', regex=False)
            df[col] = df[col].str.replace('Ã', 'Í', regex=False)
            df[col] = df[col].str.replace('Ã', 'Á', regex=False)
            df[col] = df[col].str.replace('Ã‰', 'É', regex=False)
            df[col] = df[col].str.replace('Ãš', 'Ú', regex=False)
    
    print(f"[INFO] DataFrame limpiado: {len(df)} filas finales, {len(df.columns)} columnas finales")
    
    return df

def read_excel_safe(file_obj, filename):
    """Lee un archivo Excel/CSV de forma segura, detectando formato corrupto"""
    try:
        # Leer contenido
        file_content = file_obj.read()
        file_obj.seek(0)  # Resetear posición
        
        # Detectar si es HTML disfrazado de .xls
        if filename.endswith('.xls') and is_html_file(file_content):
            # Es un archivo HTML, intentar leerlo con pandas usando read_html
            print(f"[INFO] Archivo .xls detectado como HTML, procesando como tabla HTML...")
            try:
                # Decodificar el contenido completo primero para evitar problemas de lectura parcial
                print(f"[INFO] Decodificando contenido HTML ({len(file_content)} bytes)...")
                try:
                    content_decoded = file_content.decode('latin-1', errors='ignore')
                except:
                    content_decoded = file_content.decode('cp1252', errors='ignore')
                
                print(f"[INFO] Contenido decodificado: {len(content_decoded)} caracteres")
                
                # Leer tabla HTML desde el contenido decodificado
                dfs = pd.read_html(io.StringIO(content_decoded), header=0)
                
                if len(dfs) == 0:
                    raise ValueError('No se encontraron tablas en el archivo HTML')
                
                # Usar la primera tabla encontrada y limpiar
                df = dfs[0]
                print(f"[INFO] Tabla HTML extraída: {len(df)} filas, {len(df.columns)} columnas")
                df = clean_dataframe(df)
                
                return df
                
            except Exception as e:
                raise ValueError(f'No se pudo leer el archivo HTML como tabla: {str(e)}')
        
        # Intentar leer según extensión (archivos Excel reales)
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            return clean_dataframe(df)
            
        elif filename.endswith('.xls'):
            # Intentar primero como Excel binario real (Excel 97-2003)
            try:
                print(f"[INFO] Leyendo archivo Excel 97-2003 (.xls)...")
                # Leer con xlrd
                df = pd.read_excel(
                    io.BytesIO(file_content), 
                    engine='xlrd'
                )
                
                print(f"[INFO] Excel 97-2003 leído: {len(df)} filas, {len(df.columns)} columnas")
                
                # Limpiar SOLO una vez
                return clean_dataframe(df)
                
            except Exception as e:
                # Si falla, intentar como HTML
                if 'Expected BOF record' in str(e) or 'Unsupported format' in str(e):
                    print(f"[INFO] Archivo .xls no es formato binario, intentando como HTML...")
                    try:
                        # Decodificar el contenido completo primero
                        try:
                            content_decoded = file_content.decode('latin-1', errors='ignore')
                        except:
                            content_decoded = file_content.decode('cp1252', errors='ignore')
                        
                        dfs = pd.read_html(io.StringIO(content_decoded), header=0)
                    except:
                        raise ValueError('No se pudo leer el archivo como HTML')                    
                    if len(dfs) == 0:
                        raise ValueError('No se encontraron tablas en el archivo')
                    
                    df = dfs[0]
                    df = clean_dataframe(df)
                    
                    return df
                raise
        else:
            # CSV - intentar con diferentes encodings y separadores
            print(f"[INFO] Leyendo archivo CSV...")
            try:
                # Intentar primero con UTF-8
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
                print(f"[INFO] CSV leído con UTF-8")
            except UnicodeDecodeError:
                try:
                    # Si falla, intentar con latin-1
                    df = pd.read_csv(io.BytesIO(file_content), encoding='latin-1')
                    print(f"[INFO] CSV leído con latin-1")
                except:
                    # Último intento con cp1252
                    df = pd.read_csv(io.BytesIO(file_content), encoding='cp1252')
                    print(f"[INFO] CSV leído con cp1252")
            
            # Detectar separador si es necesario
            if len(df.columns) == 1:
                # Probablemente el separador no es coma, intentar con pipe
                file_obj = io.BytesIO(file_content)
                try:
                    df = pd.read_csv(file_obj, sep='|', encoding='latin-1')
                    print(f"[INFO] CSV leído con separador '|'")
                except:
                    # Intentar detectar automáticamente
                    file_obj = io.BytesIO(file_content)
                    df = pd.read_csv(file_obj, sep=None, engine='python', encoding='latin-1')
                    print(f"[INFO] CSV leído con separador auto-detectado")
            
            return clean_dataframe(df)
            
    except Exception as e:
        raise

def save_to_cache(user_id, filename, dataframe):
    """Guarda un DataFrame en el cache del usuario (filesystem)"""
    # NO limpiar aquí - ya se limpió en read_excel_safe
    # Solo verificar que no esté vacío
    if len(dataframe) == 0:
        print(f"[WARNING] Intentando guardar DataFrame vacío!")
    
    # Convertir DataFrame a CSV en memoria
    output = io.BytesIO()
    # Usar UTF-8 con BOM para compatibilidad con Excel y caracteres especiales
    # QUOTE_MINIMAL (quoting=0) añade comillas solo donde es necesario (valores con comas)
    # La columna Venta - IVA contiene comas, así que pandas añadirá las comillas automáticamente
    dataframe.to_csv(output, index=False, encoding='utf-8-sig', sep=',', quoting=0)
    output.seek(0)
    csv_data = output.getvalue()
    
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
    
    print(f"[INFO] Archivo guardado en cache: {filename} ({len(dataframe)} filas, {len(dataframe.columns)} columnas)")
    
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

def transformar_ventas(df, mes=''):
    """
    Aplica todas las transformaciones necesarias al DataFrame de ventas
    """
    print(f"[INFO] Iniciando transformacion de ventas con mes: {mes}")
    print(f"[INFO] DataFrame inicial: {len(df)} filas, {len(df.columns)} columnas")
    
    # Verificar que existen las columnas necesarias
    columnas_requeridas = ['Cliente', 'Nombre', 'Razon Social', 'Documento', 'Barrio', 'Nombre Segmento',
                           'Producto', 'Nombre.1', 'Cant. pedida', 'Cant. devuelta', 'Cantidad neta',
                           'IVA', 'Venta - IVA', 'Marca', 'Sub marca', 'Linea', 'Sub linea',
                           'Categoria', 'Sub categoria', 'Negocio', 'Vendedor', 'Ciudad']
    
    # Verificar columnas faltantes
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if columnas_faltantes:
        print(f"[WARN] Faltan columnas: {columnas_faltantes}")
        # Usar solo las columnas disponibles
        columnas_disponibles = [col for col in columnas_requeridas if col in df.columns]
        df = df[columnas_disponibles].copy()
    else:
        # Filtrado de columnas
        df = df[columnas_requeridas].copy()
    
    print(f"[INFO] Columnas filtradas: {len(df.columns)} columnas")
    
    # Filtrar vendedor si existe la columna
    if 'Vendedor' in df.columns:
        filas_antes = len(df)
        df = df[df['Vendedor'] != '99 - SERVICIOS']
        print(f"[INFO] Filas filtradas (vendedor): {filas_antes} -> {len(df)}")
    
    # Reemplazos de valores
    reemplazos = {
        'Categoria': {
            '10-Cafi': '10-Cafe',
            '51-Ti e infusiones': '51-Te e infusiones',
            '61-Equipos Preparacisn': '61-Equipos Preparacion',
            '06-Champiqones': '06-Champinones',
            '09-Bebidas dechocolate': '09-Bebidas de chocolate',
        },
        'Nombre Segmento': {
            'Reposicisn': 'Reposicion',
            'AU Multimisisn': 'AU Multimision',
            'Servicios de Alimentacisn': 'Servicios de Alimentacion'
        },
        'Marca': {
            '026-Colcafi': '026-Colcafe',
            '001-Zenz': '001-Zenu',
            '351-Genirico otros distibuidos': '351-Generico otros distribuidos',
            '373-Binet': '373-Benet'
        },
        'Sub marca': {
            '01-Colcafi': '01-Colcafe',
            '02-Zenz': '02-Zenu',
            '01-Genirico otros distibuidos': '01-Generico otros distribuidos',
            '01-Binet': '01-Benet',
            '02-Zenz': '01-Zenu',
            '10-Lechey calcio': '10-Leche y calcio',
            '04-Lechecon almendras': '04-Leche con almendras',
            '12-Quesoy Mantequilla': '12-Queso y Mantequilla',
            '08-Gool': '08-Gol'
        },
        'Negocio': {
            '04-Cafi': '04-Cafe',
            '23-Nutricisn Experta': '23-Nutricion Experta'
        }
    }
    
    for columna, valores in reemplazos.items():
        if columna in df.columns:
            df[columna] = df[columna].replace(valores)
    
    print(f"[INFO] Reemplazos aplicados")
    
    # Insertar mes
    if mes:
        df.insert(1, 'Mes', mes)
        print(f"[INFO] Mes insertado: {mes}")
    
    # División de columnas
    if 'Vendedor' in df.columns:
        df[['Cod. Asesor', 'Asesor']] = df['Vendedor'].str.split('-', n=1, expand=True)
        df.drop(columns=['Vendedor'], inplace=True)
        print(f"[INFO] Columna Vendedor dividida")
    
    if 'Ciudad' in df.columns:
        split_result = df['Ciudad'].str.split('-', n=1, expand=True)
        if split_result.shape[1] == 2:
            df['Cod. Ciudad'] = split_result[0]
            df['Ciudad'] = split_result[1]
            # Eliminar Cod. Ciudad
            df.drop(columns=['Cod. Ciudad'], inplace=True)
            print(f"[INFO] Columna Ciudad procesada")
    
    # Formatear SOLO la columna "Venta - IVA" con coma como separador decimal
    # Las demás columnas numéricas se mantienen como números enteros
    # Las comillas se añadirán después al guardar el CSV
    if 'Venta - IVA' in df.columns:
        # Convertir a numérico si no lo es
        df['Venta - IVA'] = pd.to_numeric(df['Venta - IVA'], errors='coerce')
        # Dividir entre 100 para obtener los decimales correctos
        # Formatear con coma como separador: 1512600 / 100 = 15126.00 -> 15126,00
        df['Venta - IVA'] = df['Venta - IVA'].apply(
            lambda x: f'{x/100:.2f}'.replace('.', ',') if pd.notna(x) else ''
        )
        print(f"[INFO] Columna 'Venta - IVA' formateada con coma decimal")
    
    print(f"[INFO] Transformacion completa: {len(df)} filas, {len(df.columns)} columnas")
    
    return df

def transformar_clientes(df):
    """
    Aplica transformaciones al DataFrame de clientes
    Maneja tanto el formato de 17 columnas como el de 29 columnas
    """
    print(f"[INFO] Iniciando transformacion de clientes")
    print(f"[INFO] DataFrame inicial: {len(df)} filas, {len(df.columns)} columnas")
    
    # Detectar qué formato tiene el archivo (17 o 29 columnas)
    if 'Cod AC' in df.columns:
        # Formato completo de 29 columnas
        print(f"[INFO] Detectado formato completo (29 columnas)")
        columnas_esperadas = [
            'Cod AC', 'Codigo Ecom', 'Sucursal', 'Nombre Cliente', 'Documento',
            'Ra. Social', 'Direccion', 'Nombre Neg', 'Telefono', 'Cod Dpto', 'Dpto',
            'Cod Ciudad', 'Ciudad', 'Barrio', 'Segmento', 'Estado', 'Fecha',
            'Creacion', 'Coordenada Y', 'Coordenada X', 'Exhibidor', 'Cod.Asesor',
            'Asesor', 'Dias de visita', 'Distrito', 'Region', 'Coordenadas Gis',
            'Codigo CUP', 'Socios Nutresa'
        ]
    else:
        # Formato reducido de 17 columnas
        print(f"[INFO] Detectado formato reducido (17 columnas)")
        columnas_esperadas = [
            'Codigo Ecom', 'Sucursal', 'Documento', 'Ra. Social', 'Nombre Neg',
            'Dpto', 'Ciudad', 'Barrio', 'Segmento', 'Fecha',
            'Coordenada Y', 'Coordenada X', 'Exhibidor', 'Cod.Asesor',
            'Asesor', 'Coordenadas Gis', 'Socios Nutresa'
        ]
    
    # Verificar qué columnas existen
    columnas_disponibles = [col for col in columnas_esperadas if col in df.columns]
    columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]
    
    if columnas_faltantes:
        print(f"[WARN] Columnas faltantes (se agregarán vacías): {columnas_faltantes}")
        # Agregar columnas faltantes con valores vacíos
        for col in columnas_faltantes:
            df[col] = ''
    
    # Seleccionar solo las columnas esperadas
    df = df[columnas_esperadas].copy()
    
    print(f"[INFO] Columnas seleccionadas: {len(df.columns)} columnas")
    
    # Reemplazar NaN y 'nan' por cadenas vacías
    df = df.fillna('')
    df = df.replace('nan', '', regex=False)
    
    # Aplicar correcciones de ciudades y segmentos
    if 'Ciudad' in df.columns:
        df['Ciudad'] = df['Ciudad'].replace({'MOQITOS': 'MONITOS'})
    
    if 'Segmento' in df.columns:
        df['Segmento'] = df['Segmento'].replace({
            'Reposición': 'Reposicion',  # Con tilde también
            'Reposicisn': 'Reposicion',
            'AU Multimisisn': 'AU Multimision',
            'Servicios de Alimentacisn': 'Servicios de Alimentacion',
            'Centros de diversisn': 'Centros de diversion'
        })
    
    print(f"[INFO] Correcciones aplicadas")
    
    # Conversión de tipos (convertir NaN a string vacío primero)
    if 'Codigo Ecom' in df.columns:
        df['Codigo Ecom'] = df['Codigo Ecom'].astype(str).replace('nan', '')
    if 'Documento' in df.columns:
        df['Documento'] = df['Documento'].astype(str).replace('nan', '')
    if 'Exhibidor' in df.columns:
        df['Exhibidor'] = df['Exhibidor'].astype(str).replace('nan', '')
    if 'Cod.Asesor' in df.columns:
        df['Cod.Asesor'] = df['Cod.Asesor'].astype(str).replace('nan', '')
    
    # Formatear fechas (solo si no están vacías)
    for col_fecha in ['Fecha', 'Creacion']:
        if col_fecha in df.columns:
            df[col_fecha] = df[col_fecha].replace('', pd.NaT)
            df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
            df[col_fecha] = df[col_fecha].dt.strftime('%d-%m-%Y')
            df[col_fecha] = df[col_fecha].fillna('')
    
    print(f"[INFO] Conversiones de tipo aplicadas")
    print(f"[INFO] Transformacion completa: {len(df)} filas, {len(df.columns)} columnas")
    
    return df

def transformar_exhibidores(df):
    """
    Aplica transformaciones al DataFrame de exhibidores
    Filtra, limpia y categoriza los exhibidores
    """
    print(f"[INFO] Iniciando transformacion de exhibidores")
    print(f"[INFO] DataFrame inicial: {len(df)} filas, {len(df.columns)} columnas")
    
    # Reemplazar NaN y 'nan' por cadenas vacías
    df = df.fillna('')
    df = df.replace('nan', '', regex=False)
    
    # Conversión de tipos
    if 'Numero' in df.columns:
        df['Numero'] = df['Numero'].astype(str)
    if 'Cod. Cliente' in df.columns:
        df['Cod. Cliente'] = df['Cod. Cliente'].astype(str)
        df['Cod. Cliente'] = df['Cod. Cliente'].str.replace('.0', '', regex=False)
    if 'Num. Comodato' in df.columns:
        df['Num. Comodato'] = df['Num. Comodato'].astype(str)
        df['Num. Comodato'] = df['Num. Comodato'].str.replace(';', '', regex=False)
    
    print(f"[INFO] Conversiones de tipo aplicadas")
    
    # Eliminar columna sin nombre si existe
    if 'Unnamed: 12' in df.columns:
        df = df.drop(columns=['Unnamed: 12'])
        print(f"[INFO] Columna 'Unnamed: 12' eliminada")
    
    # Filtrar por Estado = 'A' (Activo)
    if 'Estado' in df.columns:
        filas_antes = len(df)
        df = df[df['Estado'] == 'A']
        print(f"[INFO] Filtrado por Estado='A': {filas_antes} -> {len(df)} filas")
    
    # Filtrar tipo específico
    if 'Tipo' in df.columns:
        filas_antes = len(df)
        df = df[df['Tipo'] != '40089999-MUEBLE SNACKERO ABARROTERO MOSTRADOR']
        print(f"[INFO] Filtrado tipo no deseado: {filas_antes} -> {len(df)} filas")
    
    # Crear columna Categoria
    if 'Tipo' in df.columns:
        df['Categoria'] = df['Tipo'].apply(lambda x: 'Nevera' if 'NEVERA' in str(x) else 'Snackero')
        
        # Casos especiales que son Snackero aunque tengan NEVERA en el nombre
        snackero_con_nevera = [
            '40089141-MUEBLE SNACKERO PISO GRANDE CON NEVERA',
            '40089142-MUEBLE SNACKERO PISO CON NEVERA'
        ]
        df.loc[df['Tipo'].isin(snackero_con_nevera), 'Categoria'] = 'Snackero'
        print(f"[INFO] Columna 'Categoria' creada")
    
    # Eliminar duplicados por Numero
    if 'Numero' in df.columns:
        filas_antes = len(df)
        df = df.drop_duplicates(subset=['Numero'], keep='first')
        duplicados_eliminados = filas_antes - len(df)
        if duplicados_eliminados > 0:
            print(f"[INFO] Duplicados eliminados: {duplicados_eliminados}")
    
    print(f"[INFO] Transformacion completa: {len(df)} filas, {len(df.columns)} columnas")
    
    return df

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
                # Leer archivos en memoria
                df_acum = read_excel_safe(file_acum, file_acum.filename)
                df_mes = read_excel_safe(file_mes, file_mes.filename)
                
                # Procesar: unir DataFrames
                df_resultado = pd.concat([df_acum, df_mes], ignore_index=True)
                
                # Guardar en cache
                save_to_cache(user_id, 'ventas_acum.csv', df_resultado)
                
                return jsonify({
                    'success': True, 
                    'message': 'Archivos unidos correctamente',
                    'download_url': url_for('download_file')
                })
                
            except ValueError as e:
                return jsonify({'success': False, 'error': f'Error al leer archivos: {str(e)}'}), 400
            except Exception as e:
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
            
            # Leer archivo en memoria
            df = read_excel_safe(file, file.filename)
            
            print(f"[INFO] Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
            
            # Procesar según el tipo
            if tipo == 'clientes':
                # Aplicar transformación para clientes
                print(f"[INFO] Procesando maestra de clientes")
                df_procesado = transformar_clientes(df)
                output_filename = 'maestra_clientes.csv'
                
            elif tipo == 'venta_material':
                mes = request.form.get('mes', '')
                print(f"[INFO] Procesando venta_material con mes: {mes}")
                # Aplicar transformaciones completas
                df_procesado = transformar_ventas(df, mes)
                output_filename = 'ventas_mes.csv'
            
            elif tipo == 'exhibidores':
                print(f"[INFO] Procesando exhibidores")
                # Aplicar transformaciones de exhibidores
                df_procesado = transformar_exhibidores(df)
                output_filename = 'Exhibidores.csv'
            
            else:
                return jsonify({'success': False, 'error': f'Tipo de procesamiento "{tipo}" no reconocido'}), 400
            
            print(f"[INFO] Guardando en cache: {output_filename}")
            # Guardar en cache
            save_to_cache(user_id, output_filename, df_procesado)
            
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
