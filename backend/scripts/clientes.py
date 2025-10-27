import pandas as pd
import os

def ejecutar(archivo_entrada, carpeta_salida):
    print("\n📊 Procesamiento: Base de datos de clientes")

    os.makedirs(carpeta_salida, exist_ok=True)
    archivo_salida = os.path.join(carpeta_salida, "maestra_clientes.csv")

    try:
        # Detectar extensión del archivo cargado
        extension = os.path.splitext(archivo_entrada)[1].lower()
        nombre_archivo = os.path.basename(archivo_entrada)
        print(f"✅ Archivo recibido: {nombre_archivo}")

        # Leer según el tipo de archivo
    
        if extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Codigo Ecom': str})
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, sep=None, engine="python", dtype={'Codigo Ecom': str})
        else:
            raise ValueError("❌ Formato de archivo no soportado.")

        # Columnas esperadas
        columnas = [
            'Codigo Ecom', 'Sucursal', 'Documento', 'Ra. Social', 'Nombre Neg',
            'Dpto', 'Ciudad', 'Barrio', 'Segmento', 'Fecha',
            'Coordenada Y', 'Coordenada X', 'Exhibidor', 'Cod.Asesor',
            'Asesor', 'Coordenadas Gis', 'Socios Nutresa'
        ]
        df = df[columnas].copy()

        # Correcciones
        df['Ciudad'] = df['Ciudad'].replace({'MOQITOS': 'MONITOS'})
        df['Segmento'] = df['Segmento'].replace({
            'Reposicisn': 'Reposicion',
            'AU Multimisisn': 'AU Multimision',
            'Servicios de Alimentacisn': 'Servicios de Alimentacion',
            'Centros de diversisn': 'Centros de diversion'
        })

        # Conversión de tipos
        df['Codigo Ecom'] = df['Codigo Ecom'].astype(str)
        df['Documento'] = df['Documento'].astype(str)
        df['Exhibidor'] = df['Exhibidor'].astype(str)
        df['Cod.Asesor'] = df['Cod.Asesor'].astype(str)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Fecha'] = df['Fecha'].dt.strftime('%d-%m-%Y')

        df.to_csv(archivo_salida, index=False, encoding="utf-8")
        print(f"📁 Archivo transformado guardado en: {archivo_salida}")
    
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")

