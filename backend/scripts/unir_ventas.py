"""
Script para unir ventas acumuladas con ventas del mes (transformación según especificación original)
"""
import pandas as pd
import os
import warnings

def extraer_ano_mes(df):
    """Extrae el mes de un DataFrame con columna 'Mes'"""
    if 'Mes' not in df.columns:
        raise ValueError("El archivo mensual debe contener una columna 'Mes'")
    if df['Mes'].dtype == 'O':  # object (string/fecha)
        df['Mes'] = pd.to_datetime(df['Mes'], errors='coerce')
        df['Mes'] = df['Mes'].dt.month
    return df['Mes'].unique()[0]

def leer_archivo_robusto(archivo_entrada):
    """Lee un archivo (solo .xlsx y .csv soportados)"""
    extension = os.path.splitext(archivo_entrada)[1].lower()
    
    if extension == ".xlsx":
        return pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Cliente': str, 'Documento': str})
    elif extension == ".csv":
        return pd.read_csv(archivo_entrada, sep=None, engine="python", dtype={'Cliente': str, 'Documento': str})
    else:
        raise ValueError(f"❌ Formato no soportado: {extension}. Por favor, convierta el archivo a .xlsx o .csv en Excel antes de subirlo.")

def ejecutar(archivo_acumulado, archivo_mes, carpeta_salida='transformados'):
    """
    Une el archivo de ventas acumuladas con las ventas del mes
    
    Args:
        archivo_acumulado: Ruta al archivo de ventas acumuladas
        archivo_mes: Ruta al archivo de ventas del mes
        carpeta_salida: Carpeta donde guardar el archivo transformado
    """
    try:
        print(f"\n[INFO] Procesamiento: Unión de Ventas Mensuales con Acumuladas")
        warnings.filterwarnings('ignore')
        
        # Leer archivos con conversión automática
        df_mes = leer_archivo_robusto(archivo_mes)
        print(f"[OK] Ventas del mes leidas: {len(df_mes)} registros")
        
        df_acum = leer_archivo_robusto(archivo_acumulado)
        print(f"[OK] Ventas acumuladas leidas: {len(df_acum)} registros")
        
        # Extraer mes del archivo mensual (según txt original)
        mes_nuevo = extraer_ano_mes(df_mes)
        print(f"[INFO] Mes nuevo detectado: {mes_nuevo}")
        
        # Eliminar el mes nuevo del acumulado si existe (según txt original)
        if 'Mes' not in df_acum.columns:
            raise ValueError("El archivo acumulado no contiene columna 'Mes'")
        
        df_acum = df_acum[df_acum['Mes'] != mes_nuevo]
        print(f"[INFO] Registros acumulados después de eliminar mes {mes_nuevo}: {len(df_acum)}")
        
        # Concatenar acumulado + mes (según txt original)
        df_final = pd.concat([df_acum, df_mes], ignore_index=True)
        df_final = df_final.sort_values(by='Mes')
        print(f"[INFO] Total registros después de unión: {len(df_final)}")
        
        # Guardar resultado
        archivo_salida = os.path.join(carpeta_salida, 'ventas_acum.csv')
        os.makedirs(carpeta_salida, exist_ok=True)
        df_final.to_csv(archivo_salida, index=False, encoding='utf-8')
        
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Registros procesados: {len(df_final)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
