import pandas as pd
import os

def ejecutar(archivo_entrada, carpeta_salida=None):
    print("\n📊 Procesamiento: Base de datos de clientes")

    if carpeta_salida is None:
        carpeta_salida = r'C:\Users\Jose Berrio\OneDrive\Escritorio\BI ZAFIRO 2025\Zafiro Ejecutable\Transformados'
    os.makedirs(carpeta_salida, exist_ok=True)
    archivo_salida = os.path.join(carpeta_salida, "maestra_clientes.csv")

    try:
        # Detectar extensión del archivo cargado
        extension = os.path.splitext(archivo_entrada)[1].lower()
        nombre_archivo = os.path.basename(archivo_entrada)
        print(f"✅ Archivo recibido: {nombre_archivo}")

        # Leer según el tipo de archivo
        if extension == ".xls":
            df = pd.read_excel(archivo_entrada, engine="xlrd", dtype={'Codigo Ecom': str})
        elif extension == ".xlsx":
            df = pd.read_excel(archivo_entrada, engine="openpyxl", dtype={'Codigo Ecom': str})
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, sep=None, engine="python", dtype={'Codigo Ecom': str})
        else:
            raise ValueError("❌ Formato de archivo no soportado.")

        # Columnas esperadas
        columnas = [
            'Cod AC', 'Distrito', 'Region', 'Codigo Ecom', 'Codigo CRM', 'Sucursal', 'Nombre Cliente', 'Documento',
            'Tipo de Documento', 'Ra. Social', 'Direccion', 'Nombre Neg', 'Telefono', 'Cod Dpto', 'Dpto', 'Cod Ciudad',
            'Ciudad', 'Barrio', 'Cod Canal', 'Desc Canal', 'Cod Subcanal', 'Desc SubCanal', 'Cod Tipologia', 'Desc Tipologia',
            'Segmento', 'Cod Portafolio', 'Portafolio', 'Cond Pago', 'Plazo', 'Cupo', 'Estado', 'Fecha Creacion', 'Coordenada X',
            'Coordenada Y', 'Coordenada Gis X', 'Coordenada Gis Y', 'Activo Comercial', 'Cod.Asesor', 'Cod Asesor CRM',
            'Asesor', 'Frecuencia', 'Dia', 'Orden', 'Codigo CUP', 'Socios Nutresa'
        ]

        df = df[columnas].copy()

        # Correcciones
        df['Ciudad'] = df['Ciudad'].replace({'MOQITOS': 'MONITOS'})
        df['Desc SubCanal'] = df['Desc SubCanal'].replace({
            'Reposicisn': 'Reposicion',
            'AU Multimisisn': 'AU Multimision',
            'Servicios de Alimentacisn': 'Servicios de Alimentacion',
            'Centros de diversisn': 'Centros de diversion'
        })

        # Conversión de tipos
        df['Codigo Ecom'] = df['Codigo Ecom'].astype(str)
        df['Documento'] = df['Documento'].astype(str)
        df['Activo Comercial'] = df['Activo Comercial'].astype(str)
        df['Cod.Asesor'] = df['Cod.Asesor'].astype(str)
        df['Fecha Creacion'] = pd.to_datetime(df['Fecha Creacion'], errors='coerce')
        df['Fecha Creacion'] = df['Fecha Creacion'].dt.strftime('%d-%m-%Y')

        df.to_csv(archivo_salida, index=False, encoding="utf-8")
        print(f"📁 Archivo transformado guardado en: {archivo_salida}")
    
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")

