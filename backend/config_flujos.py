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
        'columnas_requeridas': ['Cod. Asesor'],
        'columnas_opcionales': ['LV Vegetales', 'Modificadores de Leche', 'Chocolates de Mesa',
                               'Jumbo', 'Cafe Molido', 'Badia', 'Doria', 'Saltin Noel', 'La Especial', 
                               'Dux', 'Noel', 'Gol', 'Benet', 'Jet', 'Atun', 'LV Carnicos', 
                               'Mezclas Instantaneas', 'Festival', 'Ducales', 'Instantaneo', 
                               'Comarrico', 'Tosh'],
        'tabla_destino': 'metas_numericas_asesor',
        'icon': 'user-chart',
        'validacion_minima': 12
    },
    'indicadores_semanales': {
        'nombre': 'Indicadores Semanales por Asesor',
        'descripcion': 'Carga de indicadores y métricas semanales por región, empresa y asesor',
        'webhook_url': 'https://n8n.luziia.cloud/webhook/5f028c11-6836-4f39-a56f-15136cf2f5f4',
        'columnas_requeridas': ['Region', 'Empresa', 'Asesor', 'Indicador', 'Prom Sem', 'Prom Acum Mes'],
        'columnas_opcionales': ['Mes', 'Semana', 'Dias Habiles', 'Dias', 'Lunes', 'Martes', 
                               'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo', 'Total',
                               'Ao?=', 'Año', 'Year', 'Ano'],
        'tabla_destino': 'indicadores_semanales_asesor',
        'icon': 'calendar-week'
    },
    'calendario_laboral': {
        'nombre': 'Calendario Laboral',
        'descripcion': 'Carga de calendario con días laborables y festivos',
        'webhook_url': 'https://n8n.luziia.cloud/webhook/calendario-laboralfec-6780-43a8-aadd-a024cfb68002',
        'columnas_requeridas': ['Fecha', 'Dia_Semana', 'Es_Laboral'],
        'columnas_opcionales': ['Año', 'Ano', 'Year', 'Mes', 'Observacion'],
        'tabla_destino': 'calendario_laboral',
        'icon': 'calendar'
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
    
    # Validación especial: verificar que tenga al menos N columnas opcionales
    if 'validacion_minima' in flujo_config:
        columnas_opc_lower = [col.lower() for col in flujo_config['columnas_opcionales']]
        presentes = sum(1 for col_opc in columnas_opc_lower if col_opc in columnas_lower)
        
        min_requerido = flujo_config['validacion_minima']
        total_opcionales = len(flujo_config['columnas_opcionales'])
        max_faltantes = total_opcionales - min_requerido
        
        if presentes < min_requerido:
            return {
                'valido': False,
                'mensaje': f"Se requieren al menos {min_requerido} numéricas (máximo {max_faltantes} pueden faltar). Solo se encontraron {presentes}",
                'faltantes': []
            }
    
    return {
        'valido': True,
        'mensaje': 'Archivo válido',
        'faltantes': []
    }
