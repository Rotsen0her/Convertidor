"""
Script para procesar ventas por material con soporte robusto para archivos .xls (HTML y Excel binario)
"""
import pandas as pd
import os
import io

def ejecutar(archivo_entrada, mes):
    """
    Procesa un archivo de ventas por material
    
    Args:
        archivo_entrada: Ruta al archivo Excel/CSV de entrada
        mes: Mes de las ventas
    """
    print("\n[INFO] Procesamiento: Informe Venta x Material x Cliente")

    # Usar carpeta transformados en el directorio actual si no existe la ruta original
    carpeta_salida_original = r'C:\Users\Jose Berrio\OneDrive\Escritorio\BI ZAFIRO 2025\Zafiro Ejecutable\Transformados'
    
    if os.path.exists(os.path.dirname(carpeta_salida_original)):
        carpeta_salida = carpeta_salida_original
    else:
        # Usar carpeta local si no tenemos acceso a la ruta original
        carpeta_salida = os.path.join(os.path.dirname(__file__), '..', 'transformados')
        carpeta_salida = os.path.abspath(carpeta_salida)
        print(f"[INFO] Usando carpeta local: {carpeta_salida}")
    
    os.makedirs(carpeta_salida, exist_ok=True)
    archivo_salida = os.path.join(carpeta_salida, "ventas_mes.csv")

    try:
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
                    # Intentar primero con latin-1 que es más permisivo
                    try:
                        dfs = pd.read_html(io.BytesIO(file_content), header=0, encoding='latin-1')
                    except:
                        # Si falla, intentar con us-ascii o cp1252
                        dfs = pd.read_html(io.BytesIO(file_content), header=0, encoding='cp1252')
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
                
                # Eliminar columnas sin nombre
                unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
                if unnamed_cols:
                    df = df.drop(columns=unnamed_cols)
                    print(f"       Eliminadas {len(unnamed_cols)} columnas sin nombre")
                
                # Eliminar filas completamente vacías
                filas_antes = len(df)
                df = df.dropna(how='all')
                filas_eliminadas = filas_antes - len(df)
                if filas_eliminadas > 0:
                    print(f"       Eliminadas {filas_eliminadas} filas vacias")
                
                # Eliminar header duplicado en primera fila
                if len(df) > 0:
                    headers = df.columns.astype(str).str.strip().tolist()
                    first_row = df.iloc[0].astype(str).str.strip().tolist()
                    if headers == first_row:
                        df = df.iloc[1:].reset_index(drop=True)
                        print(f"       Eliminado header duplicado en primera fila")
                
                # Convertir tipos de datos apropiadamente
                for col in df.columns:
                    if 'Cliente' in col or 'Documento' in col or 'Cod' in col:
                        df[col] = df[col].astype(str)
                
                print(f"[OK] Limpieza completa: {len(df)} filas, {len(df.columns)} columnas")
            else:
                print("[INFO] Archivo .xls es Excel binario real")
                # Leer como Excel binario
                df = pd.read_excel(archivo_entrada, engine="xlrd", dtype={'Cliente': str, 'Documento': str})
                
        elif extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Cliente': str, 'Documento': str})
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, dtype={'Cliente': str, 'Documento': str}, sep=None, engine="python")
        else:
            raise ValueError("Formato no soportado.")

        print(f"\n[INFO] Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        print(f"       Columnas disponibles: {list(df.columns)}")

        # Verificar que existen las columnas necesarias
        columnas_requeridas = ['Cliente', 'Nombre', 'Razon Social', 'Documento', 'Barrio', 'Nombre Segmento',
                               'Producto', 'Nombre.1', 'Cant. pedida', 'Cant. devuelta', 'Cantidad neta',
                               'IVA', 'Venta - IVA', 'Marca', 'Sub marca', 'Linea', 'Sub linea',
                               'Categoria', 'Sub categoria', 'Negocio', 'Vendedor', 'Ciudad']
        
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            print(f"[WARN] Faltan columnas: {columnas_faltantes}")
            # Intentar encontrar columnas similares
            for col_faltante in columnas_faltantes:
                similares = [c for c in df.columns if col_faltante.lower() in c.lower()]
                if similares:
                    print(f"       Columnas similares encontradas: {similares}")

        # Filtrado de columnas (solo las que existan)
        columnas_disponibles = [col for col in columnas_requeridas if col in df.columns]
        df = df[columnas_disponibles].copy()
        
        print(f"\n[INFO] Filtrando datos...")
        print(f"       Filas antes de filtrar: {len(df)}")

        # Filtrar vendedor si la columna existe
        if 'Vendedor' in df.columns:
            df = df[df['Vendedor'] != '99 - SERVICIOS']
            print(f"       Filas despues de filtrar vendedor: {len(df)}")

        # Reemplazos
        print(f"\n[INFO] Aplicando correcciones...")
        reemplazos = {
            'Categoria': {
                '10-Cafi': '10-Cafe',
                '51-Ti e infusiones': '51-Te e infusiones',
                '61-Equipos Preparacisn': '61-Equipos Preparacion',
                '06-Champiqones': '06-Champinones',
                '09-Bebidas dechocolate': '09-Bebidas de chocolate',
            },
            'Nombre Segmento': {
                'Reposicisn': 'Reposicion',
                'AU Multimisisn': 'AU Multimision',
                'Servicios de Alimentacisn': 'Servicios de Alimentacion'
            },
            'Marca': {
                '026-Colcafi': '026-Colcafe',
                '001-Zenz': '001-Zenu',
                '351-Genirico otros distibuidos': '351-Generico otros distribuidos',
                '373-Binet': '373-Benet'
            },
            'Sub marca': {
                '01-Colcafi': '01-Colcafe',
                '02-Zenz': '02-Zenu',
                '01-Genirico otros distibuidos': '01-Generico otros distribuidos',
                '01-Binet': '01-Benet',
                '02-Zenz': '01-Zenu',
                '10-Lechey calcio': '10-Leche y calcio',
                '04-Lechecon almendras': '04-Leche con almendras',
                '12-Quesoy Mantequilla': '12-Queso y Mantequilla',
                '08-Gool': '08-Gol'
            },
            'Negocio': {
                '04-Cafi': '04-Cafe',
                '23-Nutricisn Experta': '23-Nutricion Experta'
            }
        }

        for columna, valores in reemplazos.items():
            if columna in df.columns:
                df[columna] = df[columna].replace(valores)

        # Insertar mes
        df.insert(1, 'Mes', mes)
        print(f"[OK] Mes insertado: {mes}")

        # División de columnas
        if 'Vendedor' in df.columns:
            df[['Cod. Asesor', 'Asesor']] = df['Vendedor'].str.split('-', n=1, expand=True)
            df.drop(columns=['Vendedor'], inplace=True)
            print(f"[OK] Columna Vendedor dividida en Cod. Asesor y Asesor")
        
        if 'Ciudad' in df.columns:
            split_result = df['Ciudad'].str.split('-', n=1, expand=True)
            if split_result.shape[1] == 2:
                df['Ciudad'] = split_result[1]  # Mantener solo el nombre
                print(f"[OK] Columna Ciudad procesada")

        # Formatear SOLO la columna "Venta - IVA" con coma como separador decimal
        # Las comillas se añadirán automáticamente al guardar el CSV
        print(f"\n[INFO] Formateando columna Venta - IVA...")
        if 'Venta - IVA' in df.columns:
            # Convertir a numérico si no lo es
            df['Venta - IVA'] = pd.to_numeric(df['Venta - IVA'], errors='coerce')
            # Dividir entre 100 para obtener los decimales correctos
            # Formatear con coma como separador: 1512600 / 100 = 15126.00 -> 15126,00
            df['Venta - IVA'] = df['Venta - IVA'].apply(
                lambda x: f'{x/100:.2f}'.replace('.', ',') if pd.notna(x) else ''
            )
            print(f"[OK] Columna Venta - IVA formateada")

        # Guardar archivo con coma como separador (estándar CSV)
        # QUOTE_MINIMAL (quoting=0) añade comillas solo donde es necesario (valores con comas)
        # La columna Venta - IVA contiene comas, así que pandas añadirá las comillas automáticamente
        print(f"\n[INFO] Guardando archivo transformado...")
        df.to_csv(archivo_salida, index=False, encoding='utf-8-sig', sep=',', quoting=0)
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Datos finales: {len(df)} filas, {len(df.columns)} columnas")
        
        # Mostrar preview
        print(f"\n[INFO] Preview de las primeras filas:")
        print(df.head(3).to_string())

    except Exception as e:
        print(f"\n[ERROR] Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        raise
