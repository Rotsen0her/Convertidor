import pandas as pd
import os

def ejecutar(archivo_entrada, mes, carpeta_salida):
    print("\n📦 Procesamiento: Informe Venta x Material x Cliente")

    os.makedirs(carpeta_salida, exist_ok=True)
    archivo_salida = os.path.join(carpeta_salida, "ventas_mes.csv")

    try:
        extension = os.path.splitext(archivo_entrada)[1].lower()

        # Lectura
        if extension == ".csv":
            df = pd.read_csv(archivo_entrada, dtype={'Cliente': str, 'Documento': str}, sep=',', encoding = 'latin1' , engine="python")
        else:
            raise ValueError("Formato no soportado.")

        # Renombrar columnas
        df = df.rename(columns={'Razon Soc': 'Razon Social',
                        'Cant. Ped.': 'Cant. pedida',
                        'Cant. Dev.': 'Cant. devuelta',
                        'Cant. Neta': 'Cantidad neta',
                        'Vta. - IVA': 'Venta - IVA',
                        'SubMarca': 'Sub marca',
                        'SubLinea': 'Sub linea',
                        'Sub Categoria': 'Sub categoria',
                        })

        # Filtrado de columnas
        df = df[['Cliente', 'Nombre', 'Razon Social', 'Documento','Barrio','Nombre Segmento','Producto', 'Nombre.1','Cant. pedida', 
                'Cant. devuelta', 'Cantidad neta', 'IVA','Venta - IVA','Marca', 'Sub marca','Linea', 'Sub linea', 'Categoria', 'Sub categoria', 
                'Negocio','Vendedor', 'Ciudad']].copy()

        df = df[df['Vendedor'] != '99 - SERVICIOS']

        # Reemplazos
        reemplazos = {
            'Categoria': {
                '10-Café': '10-Cafe',
                '51-Té e infusiones': '51-Te e infusiones',
                '61-Equipos Preparación': '61-Equipos Preparacion',
                '06-Champiñones': '06-Champinones',
                '09-Bebidas dechocolate': '09-Bebidas de chocolate',
            },
            'Nombre Segmento': {
                'Reposición': 'Reposicion',
                'AU Multimisión': 'AU Multimision',
                'Servicios de Alimentación': 'Servicios de Alimentacion',
                'Centros de diversión': 'Centros de diversion'
            },
            'Marca': {
                '026-Colcafé': '026-Colcafe',
                '001-Zenú': '001-Zenu',
                '351-Genérico otros distibuidos': '351-Generico otros distribuidos',
                '373-Bénet': '373-Benet',
                '113-Drácula': '113-Dracula',
                '096-Setas de Cuivá': '096-Setas de Cuiva'
            },
            'Sub marca': {
                '01-Colcafé': '01-Colcafe',
                '01-Zenú': '01-Zenu',
                '02-Zenú': '02-Zenu',
                '01-Genérico otros distibuidos': '01-Generico otros distribuidos',
                '01-Bénet': '01-Benet',
                '10-Lechey calcio': '10-Leche y calcio',
                '04-Lechecon almendras': '04-Leche con almendras',
                '12-Quesoy Mantequilla': '12-Queso y Mantequilla',
                '08-Gool': '08-Gol',
                '01-Drácula': '01-Dracula',
            },
            'Negocio': {
                '01-Cárnicos': '01-Carnicos',
                '04-Café': '04-Cafe',
                '23-Nutrición Experta': '23-Nutricion Experta',
            },
            'Linea': {
                '0094-Sólidas': '0094-Solidas',
                '0041-Azúcar': '0041-Azucar',
                '0058-Café Molido': '0058-Cafe Molido',
                '0103-Pasta Clásica': '0103-Pasta Clasica',
                '0200-Atún': '0200-Atun',
                '0194-Maíz LV': '0194-Maiz LV',
                '0029-Otros LV Cárnicos': '0029-Otros LV Carnicos',
                '0090-Cremas dechocolate': '0090-Cremas de chocolate',
                '0521-Cápsulas': '0521-Capsulas',
            },
            'Sub linea':{
                '0161-Sólidas sin agregados': '0161-Solidas sin agregados',
                '0160-Sólidas con agregados': '0160-Solidas con agregados',
                '0171-Grageadoscrocantes': '0171-Grageados crocantes',
                '0173-Clásica': '0173-Clasica',
                '0296-Maíz LV': '0296-Maiz LV',
                '0151-Bombones sólidos': '0151-Bombones solidos',
                '0420-Azúcar': '0420-Azucar',
                '0152-Cremas deChocolate': '0152-Cremas de Chocolate',
                '0141-Estuches de Línea': '0141-Estuches de Linea',
                '0688-Cápsulas': '0688-Capsulas',
            },
            'Sub categoria': {
                '026-Instantáneo': '026-Instantaneo',
                '027-Mezclas Instantáneas': '027-Mezclas Instantaneas',
                '056-OtrosDistribuidos': '056-Otros Distribuidos',
                '277-Cápsulas Nutricional': '277-Capsulas Nutricional'
            }
        
        }

        for columna, valores in reemplazos.items():
            df[columna] = df[columna].replace(valores)

        # Insertar mes
        df.insert(1, 'Mes', mes)

        # División de columnas
        df[['Cod. Asesor', 'Asesor']] = df['Vendedor'].str.split('-', expand=True)
        df[['Cod. Ciudad', 'Ciudad']] = df['Ciudad'].str.split('-', expand=True)
        df.drop(columns=['Cod. Ciudad', 'Vendedor'], inplace=True)

        # Conversion columna Venta - IVA a numero entero
        df['Venta - IVA'] = pd.to_numeric(df['Venta - IVA'], errors='coerce').fillna(0).astype(int)


        # Guardar archivo
        df.to_csv(archivo_salida, index=False, encoding='latin1')
        print(f"📁 Archivo transformado guardado en: {archivo_salida}")

    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")