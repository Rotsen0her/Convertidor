"""
Script para unir ventas acumuladas con ventas del mes (transformación según especificación original)
"""
import pandas as pd
import os
import io

def leer_archivo_robusto(archivo_entrada):
    """Lee un archivo con conversión automática de .xls a .xlsx"""
    extension = os.path.splitext(archivo_entrada)[1].lower()
    
    if extension == ".xls":
        # Convertir .xls a .xlsx internamente para evitar problemas de encoding
        print(f"[INFO] Detectado archivo .xls, convirtiendo a .xlsx internamente...")
        
        try:
            # Leer con xlrd (motor antiguo para .xls)
            df_temp = pd.read_excel(archivo_entrada, engine='xlrd', dtype={'Cliente': str, 'Documento': str})
            
            # Convertir a .xlsx en memoria usando openpyxl
            xlsx_buffer = io.BytesIO()
            with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                df_temp.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Leer el .xlsx generado
            xlsx_buffer.seek(0)
            df = pd.read_excel(xlsx_buffer, engine='openpyxl', dtype={'Cliente': str, 'Documento': str})
            
            print(f"[INFO] Conversión .xls -> .xlsx completada: {len(df)} filas, {len(df.columns)} columnas")
            
            # Limpieza mínima: solo eliminar header duplicado si existe
            if len(df) > 0:
                headers = df.columns.astype(str).tolist()
                first_row = df.iloc[0].astype(str).tolist()
                if first_row == headers:
                    df = df.iloc[1:].reset_index(drop=True)
                    print(f"[INFO] Primera fila era header duplicado, eliminada")
            
            return df
            
        except Exception as e:
            print(f"[ERROR] Error convirtiendo .xls a .xlsx: {e}")
            raise
            
    elif extension == ".xlsx":
        return pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Cliente': str, 'Documento': str})
    elif extension == ".csv":
        return pd.read_csv(archivo_entrada, sep=None, engine="python", dtype={'Cliente': str, 'Documento': str})
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
        print(f"\n[INFO] Procesamiento: Unión de Ventas Mensuales con Acumuladas")
        
        # Leer archivos con conversión automática
        df_mes = leer_archivo_robusto(archivo_mes)
        print(f"[OK] Ventas del mes leidas: {len(df_mes)} registros")
        
        df_acum = leer_archivo_robusto(archivo_acumulado)
        print(f"[OK] Ventas acumuladas leidas: {len(df_acum)} registros")
        
        # Extraer mes del archivo mensual (según txt original)
        if 'Mes' not in df_mes.columns:
            raise ValueError("El archivo mensual debe contener una columna 'Mes'")
        
        mes_nuevo = df_mes['Mes'].unique()[0]
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
        df_final.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Registros procesados: {len(df_final)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
