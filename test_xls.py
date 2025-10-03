"""
Script de prueba para diagnosticar lectura de archivos .xls
"""
import pandas as pd
import io

archivo = r"C:\Users\andre\Downloads\maestratotl20251002.xls"

print("=" * 80)
print("DIAGNÓSTICO DE ARCHIVO .xls")
print("=" * 80)

# 1. Info del archivo
import os
file_size = os.path.getsize(archivo)
print(f"\n[1] Información del archivo:")
print(f"   Ruta: {archivo}")
print(f"   Tamaño: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

# 2. Detectar tipo de archivo
print("\n[2] Detectando tipo de archivo...")
with open(archivo, 'rb') as f:
    file_content = f.read()
    header = file_content[:2048].decode('latin-1', errors='ignore').lower()
    
    is_html = any(marker in header for marker in ['<html', '<!doctype', '<htm', '<table'])
    
    if is_html:
        print("✓ Archivo detectado como: HTML disfrazado de .xls")
        print("\n[INFO] Primeros 1000 caracteres del contenido:")
        print(header[:1000])
    else:
        print("✓ Archivo detectado como: Excel binario (.xls)")

# 3. Intentar leer como HTML
if is_html:
    print("\n[3] Intentando leer como HTML...")
    try:
        # Decodificar todo el contenido primero
        print("   - Decodificando contenido completo con latin-1...")
        content_decoded = file_content.decode('latin-1', errors='ignore')
        print(f"   - Contenido decodificado: {len(content_decoded):,} caracteres")
        
        # Contar cuántas tablas hay
        table_count = content_decoded.lower().count('<table')
        print(f"   - Tablas encontradas: {table_count}")
        
        # Leer todas las tablas
        print("   - Leyendo tablas con pandas...")
        dfs = pd.read_html(io.StringIO(content_decoded), header=0)
        
        print(f"\n   ✓ Se extrajeron {len(dfs)} tabla(s)")
        
        for i, df in enumerate(dfs):
            print(f"\n   [Tabla {i+1}]")
            print(f"   - Filas: {len(df)}")
            print(f"   - Columnas: {len(df.columns)}")
            print(f"   - Columnas: {list(df.columns[:10])}")
            
            if i == 0:  # Solo mostrar detalles de la primera tabla
                print(f"\n[4] Detalles de la primera tabla:")
                print(f"   Total de filas: {len(df)}")
                print(f"   Total de columnas: {len(df.columns)}")
                
                print("\n[5] Todas las columnas:")
                for idx, col in enumerate(df.columns, 1):
                    print(f"   {idx}. {col}")
                
                print("\n[6] Primeras 5 filas:")
                print(df.head(5).to_string())
                
                print("\n[7] Verificando valores NaN por columna:")
                for col in df.columns:
                    nan_count = df[col].isna().sum()
                    if nan_count > 0:
                        porcentaje = (nan_count / len(df)) * 100
                        print(f"   {col}: {nan_count}/{len(df)} ({porcentaje:.1f}%)")
                
                print("\n[8] Guardando muestra completa (primeras 100 filas)...")
                df.head(100).to_csv('muestra_clientes_completa.csv', index=False, encoding='utf-8-sig')
                print("   ✓ Guardado: muestra_clientes_completa.csv")
        
    except Exception as e:
        print(f"   ✗ Error al leer como HTML: {e}")
        import traceback
        traceback.print_exc()

else:
    # Intentar leer como Excel binario
    print("\n[3] Intentando leer como Excel binario...")
    try:
        df = pd.read_excel(archivo, engine='xlrd')
        print(f"   ✓ Lectura exitosa: {len(df)} filas, {len(df.columns)} columnas")
        
        print("\n[4] Primeras columnas detectadas:")
        for i, col in enumerate(df.columns[:10]):
            print(f"   {i+1}. {col}")
        
        print("\n[5] Primeras 5 filas:")
        print(df.head(5))
        
    except Exception as e:
        print(f"   ✗ Error al leer como Excel: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 80)

