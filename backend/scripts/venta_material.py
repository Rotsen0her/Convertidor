"""
Script para procesar ventas por material (transformación según especificación original)
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
                    df_temp = pd.read_excel(archivo_entrada, engine='xlrd', dtype={'Cliente': str, 'Documento': str})
                    
                    # Convertir a .xlsx en memoria usando openpyxl
                    xlsx_buffer = io.BytesIO()
                    with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                        df_temp.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    # Leer el .xlsx generado
                    xlsx_buffer.seek(0)
                    df = pd.read_excel(xlsx_buffer, engine='openpyxl', dtype={'Cliente': str, 'Documento': str})
                    
                    print(f"[INFO] Conversión .xls -> .xlsx completada: {len(df)} filas, {len(df.columns)} columnas")
                    
                except Exception as e:
                    print(f"[ERROR] Error convirtiendo .xls a .xlsx: {e}")
                    raise
                
        elif extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Cliente': str, 'Documento': str})
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, dtype={'Cliente': str, 'Documento': str}, sep=None, engine="python")
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
        
        # TRANSFORMACIÓN DE VENTAS (según txt original)
        print(f"\n[INFO] Aplicando transformaciones...")

        # Filtrado de columnas (según txt original)
        columnas_requeridas = ['Cliente', 'Nombre', 'Razon Social', 'Documento', 'Barrio', 'Nombre Segmento',
                               'Producto', 'Nombre.1', 'Cant. pedida', 'Cant. devuelta', 'Cantidad neta',
                               'IVA', 'Venta - IVA', 'Marca', 'Sub marca', 'Linea', 'Sub linea',
                               'Categoria', 'Sub categoria', 'Negocio', 'Vendedor', 'Ciudad']
        
        df = df[columnas_requeridas].copy()
        print(f"[INFO] Columnas seleccionadas: {len(df.columns)} columnas")
        
        # Filtrar vendedor (según txt original)
        df = df[df['Vendedor'] != '99 - SERVICIOS']
        print(f"[INFO] Filas filtradas (vendedor): {len(df)} filas")

        # Reemplazos (según txt original)
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
            df[columna] = df[columna].replace(valores)
        
        print(f"[INFO] Reemplazos aplicados")

        # Insertar mes (según txt original)
        df.insert(1, 'Mes', mes)
        print(f"[INFO] Mes insertado: {mes}")

        # División de columnas (según txt original)
        df[['Cod. Asesor', 'Asesor']] = df['Vendedor'].str.split('-', n=1, expand=True)
        df.drop(columns=['Vendedor'], inplace=True)
        
        split_result = df['Ciudad'].str.split('-', n=1, expand=True)
        if split_result.shape[1] == 2:
            df['Ciudad'] = split_result[1]
        df.drop(columns=['Cod. Ciudad'], inplace=True, errors='ignore')
        
        print(f"[INFO] Columnas divididas")

        # Formatear SOLO la columna "Venta - IVA" con coma como separador decimal (según txt original)
        # Convertir a numérico y formatear: 1512600 / 100 = 15126.00 -> 15126,00
        df['Venta - IVA'] = pd.to_numeric(df['Venta - IVA'], errors='coerce')
        df['Venta - IVA'] = df['Venta - IVA'].apply(
            lambda x: f'{x/100:.2f}'.replace('.', ',') if pd.notna(x) else ''
        )
        print(f"[INFO] Columna 'Venta - IVA' formateada")

        # Guardar archivo
        df.to_csv(archivo_salida, index=False, encoding='utf-8-sig', sep=',', quoting=0)
        print(f"[OK] Archivo guardado: {archivo_salida}")
        print(f"[OK] Registros procesados: {len(df)}")
        
        return True

    except Exception as e:
        print(f"\n[ERROR] Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        raise
