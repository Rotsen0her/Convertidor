"""
Configuración de flujos de n8n para carga de datos a PostgreSQL
Cada flujo define las columnas esperadas y su webhook
"""
import os

FLUJOS_N8N = {
    'metas_numericas': {
        'nombre': 'Metas Numéricas',
        'descripcion': 'Carga de metas mensuales por numérica y fuerza',
        'webhook_url': os.environ.get('N8N_WEBHOOK_METAS_NUMERICAS'),
        'columnas_requeridas': ['Numerica', 'Meta'],
        'columnas_opcionales': ['Fuerza'],
        'tabla_destino': 'metas_numericas_mes',
        'icon': 'chart-bar'
    },
    'metas_asesores': {
        'nombre': 'Metas Negocios Asesores',
        'descripcion': 'Carga de presupuesto de negocios por asesor',
        'webhook_url': os.environ.get('N8N_WEBHOOK_METAS_ASESORES'),
        'columnas_requeridas': ['Cod. Asesor', 'Presupuesto'],
        'columnas_opcionales': ['Negocio', 'Negocio 2'],
        'tabla_destino': 'metas_negocios_asesores_siz',
        'icon': 'user-group'
    },
    'ventas': {
        'nombre': 'Ventas Mensuales',
        'descripcion': 'Carga de datos de ventas por cliente y producto',
        'webhook_url': os.environ.get('N8N_WEBHOOK_VENTAS'),
        'columnas_requeridas': ['Cliente', 'Mes', 'Producto', 'Venta - IVA'],
        'columnas_opcionales': ['Nombre', 'Razon Social', 'Documento', 'Barrio', 'Nombre Segmento', 
                               'Nombre.1', 'Cant. pedida', 'Cant. devuelta', 'Cantidad neta', 'IVA',
                               'Marca', 'Sub marca', 'Linea', 'Sub linea', 'Categoria', 'Sub categoria',
                               'Negocio', 'Ciudad', 'Cod. Asesor', 'Asesor'],
        'tabla_destino': 'ventas_mes_siz',
        'icon': 'currency-dollar'
    },
    'metas_numericas_asesor': {
        'nombre': 'Metas Numéricas por Asesor',
        'descripcion': 'Carga de metas mensuales por asesor y productos específicos',
        'webhook_url': os.environ.get('N8N_WEBHOOK_METAS_NUMERICAS_ASESOR'),
        'columnas_requeridas': ['Cod. Asesor', 'LV Vegetales', 'Modificadores de Leche', 'Chocolates de Mesa'],
        'columnas_opcionales': ['Jumbo', 'Cafe Molido', 'Badia', 'Doria', 'Saltin Noel', 'La Especial', 
                               'Dux', 'Noel', 'Gol', 'Benet', 'Jet', 'Atun', 'LV Carnicos', 
                               'Mezclas Instantaneas', 'Festival', 'Ducales', 'Instantaneo', 
                               'Comarrico', 'Tosh'],
        'tabla_destino': 'metas_numericas_asesor',
        'icon': 'user-chart'
    }
}

def detectar_flujo(columnas_archivo):
    """
    Detecta automáticamente qué flujo corresponde al archivo
    basándose en las columnas presentes
    
    Args:
        columnas_archivo: Lista de nombres de columnas del archivo
    
    Returns:
        tuple: (flujo_id, flujo_config) o (None, None) si no coincide
    """
    columnas_lower = [col.strip().lower() for col in columnas_archivo]
    
    # Priorizar por número de columnas coincidentes (más específico primero)
    matches = []
    
    for flujo_id, config in FLUJOS_N8N.items():
        columnas_req_lower = [col.lower() for col in config['columnas_requeridas']]
        
        # Contar cuántas columnas requeridas están presentes
        coincidencias = sum(1 for col_req in columnas_req_lower if col_req in columnas_lower)
        
        # Si TODAS las columnas requeridas están presentes
        if coincidencias == len(columnas_req_lower):
            matches.append((flujo_id, config, coincidencias))
    
    # Ordenar por más coincidencias (el más específico)
    if matches:
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches[0][0], matches[0][1]
    
    return None, None

def validar_columnas(columnas_archivo, flujo_config):
    """
    Valida que el archivo tenga las columnas necesarias
    
    Returns:
        dict: {'valido': bool, 'mensaje': str, 'faltantes': list}
    """
    columnas_lower = [col.strip().lower() for col in columnas_archivo]
    columnas_req_lower = [col.lower() for col in flujo_config['columnas_requeridas']]
    
    faltantes = [col for col in flujo_config['columnas_requeridas'] 
                 if col.lower() not in columnas_lower]
    
    if faltantes:
        return {
            'valido': False,
            'mensaje': f"Faltan columnas requeridas: {', '.join(faltantes)}",
            'faltantes': faltantes
        }
    
    return {
        'valido': True,
        'mensaje': 'Archivo válido',
        'faltantes': []
    }
