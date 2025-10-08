"""
Script para procesar archivos de clientes (transformación según especificación original)
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
        
        # Lectura según extensión
        if extension == ".xls":
            # Detectar si es HTML o Excel binario real
            print("[INFO] Detectando tipo de archivo .xls...")
            
            with open(archivo_entrada, 'rb') as f:
                file_content = f.read()
            
            # Detectar si es HTML
            header = file_content[:1024].decode('latin-1', errors='ignore').lower()
            is_html = any(marker in header for marker in ['<html', '<!doctype', '<htm', '<table'])
            
            if is_html:
                print("[INFO] Archivo .xls es HTML, extrayendo tabla...")
                try:
                    # Leer como HTML
                    dfs = pd.read_html(io.BytesIO(file_content), header=0)
                    
                    if not dfs:
                        raise ValueError("No se encontraron tablas en el archivo HTML")
                    
                    df = dfs[0]
                    print(f"[INFO] Tabla HTML extraída: {len(df)} filas, {len(df.columns)} columnas")
                    
                except ImportError as ie:
                    print(f"[ERROR] Falta dependencia para leer HTML: {ie}")
                    print("[INFO] Instale: pip install lxml html5lib")
                    raise
            else:
                # Es Excel binario real, convertir .xls a .xlsx
                print("[INFO] Archivo .xls es Excel binario, convirtiendo a .xlsx internamente...")
                
                try:
                    # Leer con xlrd (motor antiguo para .xls)
                    df_temp = pd.read_excel(archivo_entrada, engine='xlrd')
                    
                    # Convertir a .xlsx en memoria usando openpyxl
                    xlsx_buffer = io.BytesIO()
                    with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                        df_temp.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    # Leer el .xlsx generado
                    xlsx_buffer.seek(0)
                    df = pd.read_excel(xlsx_buffer, engine='openpyxl')
                    
                    print(f"[INFO] Conversión .xls -> .xlsx completada: {len(df)} filas, {len(df.columns)} columnas")
                    
                except Exception as e:
                    print(f"[ERROR] Error convirtiendo .xls a .xlsx: {e}")
                    raise
                
        elif extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl")
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, sep=None, engine="python")
        else:
            raise ValueError("Formato no soportado.")
        
        print(f"\n[INFO] Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        
        # LIMPIEZA MÍNIMA: solo eliminar header duplicado si existe
        if len(df) > 0:
            headers = df.columns.astype(str).tolist()
            first_row = df.iloc[0].astype(str).tolist()
            if first_row == headers:
                df = df.iloc[1:].reset_index(drop=True)
                print(f"[INFO] Primera fila era header duplicado, eliminada")
        
        # TRANSFORMACIÓN DE CLIENTES (según txt original)
        print(f"\n[INFO] Aplicando transformaciones...")
        
        # Columnas esperadas (17 columnas según script original)
        columnas = [
            'Codigo Ecom', 'Sucursal', 'Documento', 'Ra. Social', 'Nombre Neg',
            'Dpto', 'Ciudad', 'Barrio', 'Segmento', 'Fecha',
            'Coordenada Y', 'Coordenada X', 'Exhibidor', 'Cod.Asesor',
            'Asesor', 'Coordenadas Gis', 'Socios Nutresa'
        ]
        
        # Seleccionar columnas (sin agregar columnas faltantes, tal como en el txt)
        df = df[columnas].copy()
        
        print(f"[INFO] Columnas seleccionadas: {len(df.columns)} columnas")
        
        # Correcciones (según txt original)
        df['Ciudad'] = df['Ciudad'].replace({'MOQITOS': 'MONITOS'})
        df['Segmento'] = df['Segmento'].replace({
            'Reposicisn': 'Reposicion',
            'AU Multimisisn': 'AU Multimision',
            'Servicios de Alimentacisn': 'Servicios de Alimentacion',
            'Centros de diversisn': 'Centros de diversion'
        })
        
        print(f"[INFO] Correcciones aplicadas")
        
        # Conversión de tipos (según txt original)
        df['Codigo Ecom'] = df['Codigo Ecom'].astype(str)
        df['Documento'] = df['Documento'].astype(str)
        df['Exhibidor'] = df['Exhibidor'].astype(str)
        df['Cod.Asesor'] = df['Cod.Asesor'].astype(str)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Fecha'] = df['Fecha'].dt.strftime('%d-%m-%Y')
        
        print(f"[INFO] Conversiones de tipo aplicadas")
        
        # Guardar resultado
        archivo_salida = os.path.join(carpeta_salida, 'maestra_clientes.csv')
        os.makedirs(carpeta_salida, exist_ok=True)
        df.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Registros procesados: {len(df)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

