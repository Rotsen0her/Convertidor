"""
Script de ejemplo para procesar ventas por material
Este es un placeholder - reemplaza con tu lógica real
"""
import pandas as pd
import os

def ejecutar(archivo_entrada, mes='', carpeta_salida='transformados'):
    """
    Procesa un archivo de ventas por material
    
    Args:
        archivo_entrada: Ruta al archivo Excel/CSV de entrada
        mes: Mes de las ventas (opcional)
        carpeta_salida: Carpeta donde guardar el archivo transformado
    """
    try:
        print(f"[INFO] Procesando ventas por material: {archivo_entrada}")
        if mes:
            print(f"   Mes: {mes}")
        
        # Leer el archivo
        if archivo_entrada.endswith('.xlsx'):
            df = pd.read_excel(archivo_entrada, engine='openpyxl')
        elif archivo_entrada.endswith('.xls'):
            df = pd.read_excel(archivo_entrada, engine='xlrd')
        else:
            df = pd.read_csv(archivo_entrada)
        
        print(f"   [OK] Archivo leido: {len(df)} registros")
        
        # AQUÍ VA TU LÓGICA DE TRANSFORMACIÓN
        # Por ejemplo:
        # df_procesado = df.groupby('material')['ventas'].sum()
        # etc.
        
        # Por ahora solo copiamos el archivo
        df_procesado = df
        
        # Guardar resultado
        nombre_salida = f'venta_material_{mes}.csv' if mes else 'venta_material.csv'
        archivo_salida = os.path.join(carpeta_salida, nombre_salida)
        os.makedirs(carpeta_salida, exist_ok=True)
        df_procesado.to_csv(archivo_salida, index=False)
        
        print(f"   [OK] Archivo guardado: {archivo_salida}")
        print(f"   [OK] Registros procesados: {len(df_procesado)}")
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        raise
