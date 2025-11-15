import pandas as pd
import warnings
import os

def extraer_ano_mes(df):
    """Extrae el mes de un DataFrame con columna 'Mes'"""
    if 'Mes' not in df.columns:
        raise ValueError("El archivo mensual debe contener una columna 'Mes'")
    if df['Mes'].dtype == 'O':  # object
        df['Mes'] = pd.to_datetime(df['Mes'], errors='coerce')
        df['Mes'] = df['Mes'].dt.month
    return df['Mes'].unique()[0]

def ejecutar(archivo_acum, archivo_mes, carpeta_salida):
    print("\n🔗 Procesamiento: Unión de Ventas Mensuales con Acumuladas")
    warnings.filterwarnings('ignore')

    try:
        # Multi-encoding fallback para archivo mes
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                df_mes = pd.read_csv(archivo_mes, dtype={'Cliente': str, 'Documento': str}, encoding=encoding)
                print(f"[INFO] Archivo mes leído con encoding: {encoding}")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            raise ValueError("No se pudo leer archivo_mes con los encodings disponibles.")
        
        # Multi-encoding fallback para archivo acumulado
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                df_acum = pd.read_csv(archivo_acum, dtype={'Cliente': str, 'Documento': str}, encoding=encoding)
                print(f"[INFO] Archivo acum leído con encoding: {encoding}")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            raise ValueError("No se pudo leer archivo_acum con los encodings disponibles.")

        mes_nuevo = extraer_ano_mes(df_mes)

        if 'Mes' not in df_acum.columns:
            raise ValueError("El archivo acumulado no contiene columna 'Mes'")

        df_acum = df_acum[df_acum['Mes'] != mes_nuevo]

        df_final = pd.concat([df_acum, df_mes], ignore_index=True)
        df_final = df_final.sort_values(by='Mes')

        # Preparar carpeta de salida
        os.makedirs(carpeta_salida, exist_ok=True)
        ruta_salida = os.path.join(carpeta_salida, "ventas_acum.csv")

        df_final.to_csv(ruta_salida, index=False, encoding='utf-8')
        print(f"✅ Archivo actualizado guardado en: {ruta_salida}")

    except Exception as e:
        print(f"❌ Error durante la unión: {e}")
        raise  # Muy importante: relanzar para que la interfaz lo capture
