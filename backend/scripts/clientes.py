"""
Script para procesar archivos de clientes (transformación según especificación original)
"""
import pandas as pd
import os

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
        
        # Lectura según extensión (solo .xlsx y .csv soportados)
        if extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Codigo Ecom': str})
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, sep=None, engine="python", dtype={'Codigo Ecom': str})
        else:
            raise ValueError(f"❌ Formato no soportado: {extension}. Por favor, convierta el archivo a .xlsx o .csv en Excel antes de subirlo.")
        
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
        
        # Formatear fecha (convertir a string primero si no lo es)
        df['Fecha'] = df['Fecha'].astype(str)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Fecha'] = df['Fecha'].dt.strftime('%d-%m-%Y')
        # Reemplazar NaT por cadena vacía
        df['Fecha'] = df['Fecha'].fillna('')
        
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

