"""
Script para procesar archivos de clientes con soporte robusto para archivos .xls (HTML y Excel binario)
"""
import pandas as pd
import os
import io

def ejecutar(archivo_entrada, carpeta_salida='transformados'):
    """
    Procesa un archivo de clientes y genera la maestra
    
    Args:
        archivo_entrada: Ruta al archivo Excel/CSV de entrada
        carpeta_salida: Carpeta donde guardar el archivo transformado
    """
    try:
        print(f"\n[INFO] Procesando archivo de clientes: {archivo_entrada}")
        
        extension = os.path.splitext(archivo_entrada)[1].lower()
        
        # Lectura mejorada para .xls (detecta si es HTML o Excel real)
        if extension == ".xls":
            print("[INFO] Detectando tipo de archivo .xls...")
            
            # Leer contenido para detectar tipo
            with open(archivo_entrada, 'rb') as f:
                file_content = f.read()
            
            # Detectar si es HTML
            header = file_content[:1024].decode('latin-1', errors='ignore').lower()
            is_html = any(marker in header for marker in ['<html', '<!doctype', '<htm', '<table'])
            
            if is_html:
                print("[INFO] Archivo .xls es HTML, extrayendo tabla...")
                # Leer como HTML con manejo robusto de encoding
                try:
                    # Decodificar el contenido completo primero para evitar lectura parcial
                    print(f"[INFO] Decodificando contenido HTML ({len(file_content)} bytes)...")
                    try:
                        content_decoded = file_content.decode('latin-1', errors='ignore')
                    except:
                        content_decoded = file_content.decode('cp1252', errors='ignore')
                    
                    print(f"[INFO] Contenido decodificado: {len(content_decoded)} caracteres")
                    dfs = pd.read_html(io.StringIO(content_decoded), header=0)
                except ImportError as ie:
                    print(f"[ERROR] Falta dependencia para leer HTML: {ie}")
                    print("[INFO] Instale: pip install lxml html5lib")
                    raise
                
                if not dfs:
                    raise ValueError("No se encontraron tablas en el archivo HTML")
                df = dfs[0]
                
                print(f"[INFO] Tabla HTML extraida: {len(df)} filas, {len(df.columns)} columnas")
                
                # Limpiar datos de HTML
                print("[INFO] Limpiando datos extraidos...")
                unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
                if unnamed_cols:
                    df = df.drop(columns=unnamed_cols)
                    print(f"       Eliminadas {len(unnamed_cols)} columnas sin nombre")
                
                filas_antes = len(df)
                df = df.dropna(how='all')
                filas_eliminadas = filas_antes - len(df)
                if filas_eliminadas > 0:
                    print(f"       Eliminadas {filas_eliminadas} filas vacias")
                
                if len(df) > 0:
                    headers = df.columns.astype(str).str.strip().tolist()
                    first_row = df.iloc[0].astype(str).str.strip().tolist()
                    if headers == first_row:
                        df = df.iloc[1:].reset_index(drop=True)
                        print(f"       Eliminado header duplicado en primera fila")
                
                # Limpiar caracteres mal codificados
                print("[INFO] Limpiando caracteres mal codificados...")
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].astype(str).str.replace('Ã', 'A', regex=False)
                        df[col] = df[col].str.replace('Ã', 'O', regex=False)
                        df[col] = df[col].str.replace('Ã', 'I', regex=False)
                        df[col] = df[col].str.replace('Ã±', 'ñ', regex=False)
                        df[col] = df[col].str.replace('Ã³', 'ó', regex=False)
                        df[col] = df[col].str.replace('Ã­', 'í', regex=False)
                        df[col] = df[col].str.replace('Ã¡', 'á', regex=False)
                        df[col] = df[col].str.replace('Ã©', 'é', regex=False)
                        df[col] = df[col].str.replace('Ãº', 'ú', regex=False)
                
                print(f"[OK] Limpieza completa: {len(df)} filas, {len(df.columns)} columnas")
            else:
                print("[INFO] Archivo .xls es Excel binario real")
                df = pd.read_excel(archivo_entrada, engine="xlrd")
                
        elif extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl")
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, sep=None, engine="python")
        else:
            raise ValueError("Formato no soportado.")
        
        print(f"\n[INFO] Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        
        # TRANSFORMACIÓN DE CLIENTES
        print(f"\n[INFO] Aplicando transformaciones...")
        
        # Columnas esperadas (17 columnas según script original)
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
        df_procesado = df[columnas_esperadas].copy()
        
        print(f"[INFO] Columnas seleccionadas: {len(df_procesado.columns)} columnas")
        
        # Reemplazar NaN y 'nan' por cadenas vacías
        df_procesado = df_procesado.fillna('')
        df_procesado = df_procesado.replace('nan', '', regex=False)
        
        # Aplicar correcciones de ciudades y segmentos
        df_procesado['Ciudad'] = df_procesado['Ciudad'].replace({'MOQITOS': 'MONITOS'})
        
        df_procesado['Segmento'] = df_procesado['Segmento'].replace({
            'Reposición': 'Reposicion',  # Con tilde también
            'Reposicisn': 'Reposicion',
            'AU Multimisisn': 'AU Multimision',
            'Servicios de Alimentacisn': 'Servicios de Alimentacion',
            'Centros de diversisn': 'Centros de diversion'
        })
        
        print(f"[INFO] Correcciones aplicadas")
        
        # Conversión de tipos (convertir NaN a string vacío primero)
        df_procesado['Codigo Ecom'] = df_procesado['Codigo Ecom'].astype(str).replace('nan', '')
        df_procesado['Documento'] = df_procesado['Documento'].astype(str).replace('nan', '')
        df_procesado['Exhibidor'] = df_procesado['Exhibidor'].astype(str).replace('nan', '')
        df_procesado['Cod.Asesor'] = df_procesado['Cod.Asesor'].astype(str).replace('nan', '')
        
        # Formatear fecha (solo si no está vacía)
        df_procesado['Fecha'] = df_procesado['Fecha'].replace('', pd.NaT)
        df_procesado['Fecha'] = pd.to_datetime(df_procesado['Fecha'], errors='coerce')
        df_procesado['Fecha'] = df_procesado['Fecha'].dt.strftime('%d-%m-%Y')
        df_procesado['Fecha'] = df_procesado['Fecha'].fillna('')
        
        print(f"[INFO] Conversiones de tipo aplicadas")
        
        # Guardar resultado
        archivo_salida = os.path.join(carpeta_salida, 'maestra_clientes.csv')
        os.makedirs(carpeta_salida, exist_ok=True)
        df_procesado.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Registros procesados: {len(df_procesado)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

