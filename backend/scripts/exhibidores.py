import os
import glob
import pandas as pd
import numpy as np

def ejecutar(archivo_entrada, carpeta_salida):
    print("\n📊 Procesamiento: Base de datos de exhibidores")

    
    os.makedirs(carpeta_salida, exist_ok=True)
    archivo_salida = os.path.join(carpeta_salida, "Exhibidores.csv")

    try:
        extension = os.path.splitext(archivo_entrada)[1].lower()
        

        # Leer el archivo CSV con encoding adecuado
        if extension != ".csv":
            raise ValueError("Formato no soportado.")
        elif extension == ".csv":
            df = pd.read_csv(archivo_entrada, sep='|', encoding='utf-8', dtype={'Numero': str,'Cod. Cliente': str})

        # Correcciones y transformaciones
        df['Numero'] = df['Numero'].astype(str)
        df['Cod. Cliente'] = df['Cod. Cliente'].astype(str)
        df['Num. Comodato'] = df['Num. Comodato'].astype(str)

        if 'Unnamed: 12' in df.columns:
            df = df.drop(columns=['Unnamed: 12'])

        df['Num. Comodato'] = df['Num. Comodato'].str.replace(';', '')
        df = df[df['Estado'] == 'A']
        df = df[df['Tipo'] != '40089999-MUEBLE SNACKERO ABARROTERO MOSTRADOR']

        df['Categoria'] = np.where(df['Tipo'].str.contains('NEVERA'), 'Nevera', 'Snackero')
        df.loc[df['Tipo'].isin([
            '40089141-MUEBLE SNACKERO PISO GRANDE CON NEVERA',
            '40089142-MUEBLE SNACKERO PISO CON NEVERA'
        ]), 'Categoria'] = 'Snackero'

        df['Cod. Cliente'] = df['Cod. Cliente'].str.replace('.0', '', regex=False)
        df.drop_duplicates(subset=['Numero'], inplace=True)

        df.to_csv(archivo_salida, index=False)
        print(f"📁 Archivo transformado guardado en: {archivo_salida}")

    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
