"""
Script de ejemplo para unir ventas acumuladas con ventas del mes
Este es un placeholder - reemplaza con tu lógica real
"""
import pandas as pd
import os

def ejecutar(archivo_acumulado, archivo_mes, carpeta_salida='transformados'):
    """
    Une el archivo de ventas acumuladas con las ventas del mes
    
    Args:
        archivo_acumulado: Ruta al archivo de ventas acumuladas
        archivo_mes: Ruta al archivo de ventas del mes
        carpeta_salida: Carpeta donde guardar el archivo transformado
    """
    try:
        print(f"[INFO] Uniendo archivos de ventas")
        print(f"   Acumulado: {archivo_acumulado}")
        print(f"   Mes: {archivo_mes}")
        
        # Leer archivos
        if archivo_acumulado.endswith('.xlsx'):
            df_acum = pd.read_excel(archivo_acumulado, engine='openpyxl')
        elif archivo_acumulado.endswith('.xls'):
            df_acum = pd.read_excel(archivo_acumulado, engine='xlrd')
        else:
            df_acum = pd.read_csv(archivo_acumulado)
            
        if archivo_mes.endswith('.xlsx'):
            df_mes = pd.read_excel(archivo_mes, engine='openpyxl')
        elif archivo_mes.endswith('.xls'):
            df_mes = pd.read_excel(archivo_mes, engine='xlrd')
        else:
            df_mes = pd.read_csv(archivo_mes)
        
        print(f"   [OK] Acumulado: {len(df_acum)} registros")
        print(f"   [OK] Mes: {len(df_mes)} registros")
        
        # AQUÍ VA TU LÓGICA DE TRANSFORMACIÓN
        # Por ejemplo:
        # df_resultado = pd.concat([df_acum, df_mes], ignore_index=True)
        # df_resultado = df_resultado.drop_duplicates()
        # etc.
        
        # Por ahora concatenamos simplemente
        df_resultado = pd.concat([df_acum, df_mes], ignore_index=True)
        
        # Guardar resultado
        archivo_salida = os.path.join(carpeta_salida, 'ventas_acum.csv')
        os.makedirs(carpeta_salida, exist_ok=True)
        df_resultado.to_csv(archivo_salida, index=False)
        
        print(f"   [OK] Archivo guardado: {archivo_salida}")
        print(f"   [OK] Total registros: {len(df_resultado)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise
