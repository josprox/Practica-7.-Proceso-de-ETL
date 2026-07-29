import re
from datetime import datetime

def comillas_sql(valor):
    """
    Escapa comillas sencillas para consultas SQL seguras.
    """
    if valor is None:
        return "NULL"
    valor_str = str(valor).replace("'", "''")
    return f"'{valor_str}'"

def parsear_monto(valor_raw):
    """
    Limpia y convierte montos numéricos ('$800', 'MXN 900') a float.
    """
    if not valor_raw or str(valor_raw).strip().lower() == 'no definido':
        return None
    limpio = re.sub(r'[^\d.]', '', str(valor_raw))
    try:
        return float(limpio)
    except ValueError:
        return None

def parsear_fecha(valor_raw):
    """
    Normaliza fechas diversas al formato YYYY-MM-DD.
    """
    if not valor_raw or 'mala' in str(valor_raw).lower():
        return None
    val_str = str(valor_raw).strip()
    formatos = ('%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y')
    for fmt in formatos:
        try:
            return datetime.strptime(val_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None

def normalizar_ciudad(ciudad_raw):
    """
    Normaliza nombres de ciudades e entidades federativas en México.
    """
    c = (ciudad_raw or '').strip().lower()
    if c in ['cdmx', 'ciudad de méxico', 'ciudad de mexico', 'ciudad de mxico']:
        return 'Ciudad de México'
    elif c in ['nuevo león', 'nuevo leon', 'nuevo len', 'monterrey']:
        return 'Nuevo León'
    elif c in ['estado de méxico', 'estado de mexico', 'edomex', 'tlalnepantla', 'atizapán', 'atizapn', 'toluca']:
        return 'Estado de México'
    elif c in ['puebla', 'pue.']:
        return 'Puebla'
    elif c in ['jalisco', 'guadalajara']:
        return 'Jalisco'
    elif c in ['querétaro', 'queretaro', 'qro.']:
        return 'Querétaro'
    return ciudad_raw.strip() if ciudad_raw else 'Desconocida'

def normalizar_canal(canal_raw):
    """
    Estandariza los nombres de canales de mercadotecnia.
    """
    c = (canal_raw or '').strip().lower()
    if c in ['ig', 'instagram']:
        return 'Instagram'
    elif c in ['fb', 'facebook']:
        return 'Facebook'
    elif c in ['web', 'sitio web']:
        return 'Sitio Web'
    elif c in ['google ads']:
        return 'Google Ads'
    elif c in ['referido']:
        return 'Referido'
    return canal_raw.strip().title() if canal_raw else 'Desconocido'

def normalizar_modalidad(modalidad_raw):
    """
    Estandariza las modalidades de impartición de cursos.
    """
    mod = (modalidad_raw or '').strip().lower()
    if 'vivo' in mod:
        return 'En vivo'
    elif 'grab' in mod:
        return 'Grabado'
    elif 'hib' in mod or 'híb' in mod:
        return 'Híbrido'
    return modalidad_raw.strip().title() if modalidad_raw else 'No definida'
