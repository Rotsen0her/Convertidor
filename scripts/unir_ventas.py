"""
Script para unir ventas acumuladas con ventas del mes con soporte robusto para archivos .xls (HTML y Excel binario)
"""
import pandas as pd
import os
import io

def leer_archivo_robusto(archivo_entrada):
    """Lee un archivo con detección automática de formato HTML vs Excel binario"""
    extension = os.path.splitext(archivo_entrada)[1].lower()
    
    if extension == ".xls":
        print(f"[INFO] Detectando tipo de archivo .xls: {os.path.basename(archivo_entrada)}")
        
        with open(archivo_entrada, 'rb') as f:
            file_content = f.read()
        
        header = file_content[:1024].decode('latin-1', errors='ignore').lower()
        is_html = any(marker in header for marker in ['<html', '<!doctype', '<htm', '<table'])
        
        if is_html:
            print("[INFO] Archivo .xls es HTML, extrayendo tabla...")
            try:
                dfs = pd.read_html(io.BytesIO(file_content), header=0, encoding='latin-1')
            except:
                dfs = pd.read_html(io.BytesIO(file_content), header=0, encoding='cp1252')
            
            if not dfs:
                raise ValueError("No se encontraron tablas en el archivo HTML")
            df = dfs[0]
            
            # Limpiar datos de HTML
            unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
            if unnamed_cols:
                df = df.drop(columns=unnamed_cols)
            
            df = df.dropna(how='all')
            
            if len(df) > 0:
                headers = df.columns.astype(str).str.strip().tolist()
                first_row = df.iloc[0].astype(str).str.strip().tolist()
                if headers == first_row:
                    df = df.iloc[1:].reset_index(drop=True)
            
            print(f"[OK] Tabla extraida: {len(df)} filas, {len(df.columns)} columnas")
            return df
        else:
            print("[INFO] Archivo .xls es Excel binario real")
            return pd.read_excel(archivo_entrada, engine="xlrd")
            
    elif extension == ".xlsx":
        return pd.read_excel(archivo_entrada, engine="openpyxl")
    elif extension == ".csv":
        return pd.read_csv(archivo_entrada, sep=None, engine="python")
    else:
        raise ValueError("Formato no soportado.")

def ejecutar(archivo_acumulado, archivo_mes, carpeta_salida='transformados'):
    """
    Une el archivo de ventas acumuladas con las ventas del mes
    
    Args:
        archivo_acumulado: Ruta al archivo de ventas acumuladas
        archivo_mes: Ruta al archivo de ventas del mes
        carpeta_salida: Carpeta donde guardar el archivo transformado
    """
    try:
        print(f"\n[INFO] Uniendo archivos de ventas")
        print(f"       Acumulado: {archivo_acumulado}")
        print(f"       Mes: {archivo_mes}")
        
        # Leer archivos con detección automática
        df_acum = leer_archivo_robusto(archivo_acumulado)
        print(f"[OK] Acumulado leido: {len(df_acum)} registros")
        
        df_mes = leer_archivo_robusto(archivo_mes)
        print(f"[OK] Mes leido: {len(df_mes)} registros")
        
        # AQUÍ VA TU LÓGICA DE TRANSFORMACIÓN
        # Por ejemplo:
        # df_resultado = pd.concat([df_acum, df_mes], ignore_index=True)
        # df_resultado = df_resultado.drop_duplicates()
        # etc.
        
        # Por ahora concatenamos simplemente
        df_resultado = pd.concat([df_acum, df_mes], ignore_index=True)
        
        # Guardar resultado con encoding correcto
        archivo_salida = os.path.join(carpeta_salida, 'ventas_acum.csv')
        os.makedirs(carpeta_salida, exist_ok=True)
        df_resultado.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Total registros: {len(df_resultado)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

