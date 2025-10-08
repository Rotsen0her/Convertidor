"""
Script para procesar exhibidores (transformación según especificación original)
"""
import pandas as pd
import numpy as np
import os
import io

def ejecutar(archivo_entrada, carpeta_salida='transformados'):
    """
    Procesa un archivo de exhibidores
    
    Args:
        archivo_entrada: Ruta al archivo Excel/CSV de entrada
        carpeta_salida: Carpeta donde guardar el archivo transformado
    """
    try:
        print(f"\n[INFO] Procesamiento: Base de datos de exhibidores")
        
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
                    df_temp = pd.read_excel(archivo_entrada, engine='xlrd', dtype={'Numero': str, 'Cod. Cliente': str})
                    
                    # Convertir a .xlsx en memoria usando openpyxl
                    xlsx_buffer = io.BytesIO()
                    with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                        df_temp.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    # Leer el .xlsx generado
                    xlsx_buffer.seek(0)
                    df = pd.read_excel(xlsx_buffer, engine='openpyxl', dtype={'Numero': str, 'Cod. Cliente': str})
                    
                    print(f"[INFO] Conversión .xls -> .xlsx completada: {len(df)} filas, {len(df.columns)} columnas")
                    
                except Exception as e:
                    print(f"[ERROR] Error convirtiendo .xls a .xlsx: {e}")
                    raise
                
        elif extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Numero': str, 'Cod. Cliente': str})
        elif extension == ".csv":
            # Leer CSV con separador '|' según el txt original
            df = pd.read_csv(archivo_entrada, sep='|', encoding='latin1', dtype={'Numero': str, 'Cod. Cliente': str})
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
        
        # TRANSFORMACIÓN DE EXHIBIDORES (según txt original)
        print(f"\n[INFO] Aplicando transformaciones...")
        
        # Conversión de tipos (según txt original)
        df['Numero'] = df['Numero'].astype(str)
        df['Cod. Cliente'] = df['Cod. Cliente'].astype(str)
        df['Num. Comodato'] = df['Num. Comodato'].astype(str)
        
        # Eliminar columna sin nombre si existe (según txt original)
        if 'Unnamed: 12' in df.columns:
            df = df.drop(columns=['Unnamed: 12'])
            print(f"[INFO] Columna 'Unnamed: 12' eliminada")
        
        # Limpiar Num. Comodato (según txt original)
        df['Num. Comodato'] = df['Num. Comodato'].str.replace(';', '', regex=False)
        
        # Filtrar por Estado = 'A' (según txt original)
        df = df[df['Estado'] == 'A']
        print(f"[INFO] Filtrado por Estado='A': {len(df)} filas")
        
        # Filtrar tipo no deseado (según txt original)
        df = df[df['Tipo'] != '40089999-MUEBLE SNACKERO ABARROTERO MOSTRADOR']
        print(f"[INFO] Filtrado tipo no deseado: {len(df)} filas")
        
        # Crear columna Categoria (según txt original)
        df['Categoria'] = np.where(df['Tipo'].str.contains('NEVERA'), 'Nevera', 'Snackero')
        
        # Casos especiales que son Snackero aunque tengan NEVERA en el nombre (según txt original)
        df.loc[df['Tipo'].isin([
            '40089141-MUEBLE SNACKERO PISO GRANDE CON NEVERA',
            '40089142-MUEBLE SNACKERO PISO CON NEVERA'
        ]), 'Categoria'] = 'Snackero'
        
        print(f"[INFO] Columna 'Categoria' creada")
        
        # Limpiar Cod. Cliente (según txt original)
        df['Cod. Cliente'] = df['Cod. Cliente'].str.replace('.0', '', regex=False)
        
        # Eliminar duplicados por Numero (según txt original)
        filas_antes = len(df)
        df = df.drop_duplicates(subset=['Numero'], keep='first')
        duplicados_eliminados = filas_antes - len(df)
        if duplicados_eliminados > 0:
            print(f"[INFO] Duplicados eliminados: {duplicados_eliminados}")
        
        # Guardar resultado
        archivo_salida = os.path.join(carpeta_salida, 'Exhibidores.xlsx')
        os.makedirs(carpeta_salida, exist_ok=True)
        df.to_excel(archivo_salida, index=False)
        
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Registros procesados: {len(df)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
