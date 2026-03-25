import re
import unicodedata

COUNTRY_MAP = {
    'CL': 'CL', 'CHI': 'CL', 'CHILE': 'CL', 'CH': 'CL',
    'PE': 'PE', 'PERU': 'PE', 'PER': 'PE',
    'AR': 'AR', 'ARG': 'AR', 'ARGENTINA': 'AR',
    'CO': 'CO', 'COL': 'CO', 'COLOMBIA': 'CO',
    'CR': 'CR', 'COSTA RICA': 'CR',
    'MX': 'MX', 'MEX': 'MX', 'MEXICO': 'MX',
    'SV': 'SV', 'EL SALVADOR': 'SV',
    'PR': 'PR', 'PUERTO RICO': 'PR',
    'UR': 'UY', 'URU': 'UY', 'URUGUAY': 'UY',
    'BOL': 'BO', 'BOLIVIA': 'BO',
    'GT': 'GT', 'GUATEMALA': 'GT',
    'HN': 'HN', 'HON': 'HN', 'HONDURAS': 'HN',
    'US': 'US', 'USA': 'US', 'EEUU': 'US',
    'ITA': 'IT', 'ITALIA': 'IT',
    'UK': 'UK', 'GB': 'UK', 
    'CAN': 'CA', 'CANADA': 'CA',
    'PT': 'PT', 'PORTUGAL': 'PT',
    'PY': 'PY', 'PARAGUAY': 'PY',
    'ES': 'ES', 'ESP': 'ES', 'ESPANA': 'ES',
    'PANAMA': 'PA',
    'BR': 'BR', 'BRA': 'BR', 'BRASIL': 'BR',
    'EC': 'EC', 'ECU': 'EC', 'ECUADOR': 'EC',
    'VE': 'VE', 'VEN': 'VE', 'VZL': 'VE', 'VENEZUELA': 'VE',
    'DO': 'DO', 'DOM': 'DO', 'RD': 'DO', 'R DOM': 'DO', 'REP DOMINICANA': 'DO',
    'NI': 'NI', 'NIC': 'NI', 'NICARAGUA': 'NI',
    'CU': 'CU', 'CUB': 'CU', 'CUBA': 'CU'
}

# ==========================================
# FUNCIONES COMPARTIDAS Y VOD (Movies/Series)
# ==========================================

def remove_emojis(text: str) -> str:
    """Uso principal: Movies y Series."""
    if not text:
        return ""
    return re.sub(r"[^\w\s\-\|\/&]", "", text)

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def extract_year(text: str):
    match = re.search(r"\(?\b(19|20)\d{2}\b\)?", text)
    return int(match.group(0).strip("()")) if match else None

def remove_year(text: str):
    return re.sub(r"[\(\[\- ]?(19|20)\d{2}[\)\]]?", "", text)

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
    
def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def extract_quality(text: str):
    match = re.search(r"\b(FHD|HD|SD|4K|1080[pi]|720[pi]|480[pi]|220[pi]|HEVC|H?265)\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else None

def remove_quality(text: str) -> str:
    return re.sub(r"\b(FHD|HD|SD|4K|1080[pi]|720[pi]|480[pi]|220[pi]|HEVC|H?265)\b", "", text, flags=re.IGNORECASE).strip() if text else ""


# ==========================================
# FUNCIONES ESPECÍFICAS PARA LIVE TV
# ==========================================

def clean_obfuscation(text: str) -> str:
    if not text:
        return ""
    
    text = text.replace('ᶠ', 'F').replace('ᴴ', 'H').replace('ᴰ', 'D').replace('¹', ' 1 ')
    text = re.sub(r'(?i)(?<=[A-Z])(FHD|HD|SD|4K|HEVC)\b', r' \1', text)
    
    text = re.sub(r'(?i)Ty€', 'TYC', text)
    text = re.sub(r'(?i)C1NEMAX', 'CINEMAX', text)
    text = re.sub(r'(?i)Ŕ3@L M@DRÏD', 'REAL MADRID', text)
    text = re.sub(r'(?i)D[3E]P[OÖØ0]RT[E3]S', 'DEPORTES', text)
    text = re.sub(r'(?i)5PORT5', 'SPORTS', text)
    text = re.sub(r'(?i)[\$€][ŠS]PN', 'ESPN', text) 
    text = re.sub(r'(?i)F0X', 'FOX', text)
    text = re.sub(r'(?i)C4N4L', 'CANAL', text)
    text = re.sub(r'(?i)CUZC0', 'CUZCO', text)

    text = re.sub(r'(?i)4M[EÉ]R1C4', 'AMERICA', text)
    text = re.sub(r'(?i)4M[EÉ]RICA', 'AMERICA', text)
    text = re.sub(r'(?i)T3L3F[EÉ]', 'TELEFE', text)
    text = re.sub(r'(?i)UN1V1S1[OÖ0]N', 'UNIVISION', text)
    text = re.sub(r'(?i)T3L3MUND0', 'TELEMUNDO', text)
    text = re.sub(r'(?i)D1R3CTV', 'DIRECTV', text)
    text = re.sub(r'(?i)M[EÉ]G4', 'MEGA', text)
    text = re.sub(r'(?i)GL0B0', 'GLOBO', text)
    
    leet_map = {'$': 'S', 'Š': 'S', 'Ə': 'E', '€': 'E', 'Ö': 'O', 'Ø': 'O', '⚽': 'O', '@': 'A', 'Æ': 'A', 'Ï': 'I'}
    for bad, good in leet_map.items():
        text = text.replace(bad, good)

    
    text = re.sub(r'[^\w\s\-\(\)/|:=.]', '', text)
    
    text = re.sub(r'(?i)\b(ESPN)(\d+)\b', r'\1 \2', text)
    text = re.sub(r'(?i)\b(ESPN|FOX|HBO|STAR|TNT)\s*(?:\|\||\||=|·)\s*(EXTRA|PREMIUM|DEPORTES|SPORTS|MOVIES|ACTION|FAMILY|COMEDY|SERIES|\d+)\b', r'\1 \2', text)
        
    text = re.sub(r'\bSSPORTS\b', 'SPORTS', text, flags=re.IGNORECASE)
    text = re.sub(r'\bSSPN\b', 'ESPN', text, flags=re.IGNORECASE)

    return text

def extract_prefix(text: str):

    if re.search(r'(?i)\bvs\b', text):
        return None, text
        
    match = re.match(r'^(.{1,20}?)\s*(?:\|\||\||=|(?<!\d):(?!\d)|·)\s*(.*)', text)
    if match:
        prefix = match.group(1).strip()
        rest = match.group(2).strip()
        return prefix, rest
    return None, text

def extract_strict_country(text: str):
    """Extrae el país y lo normaliza a su código de 2 letras."""
    if not text:
        return None
    
    pattern = r"\b(CL|CHI|CHILE|CH|PE|PER[UÚ]|PER|AR|ARG|ARGENTINA|CO|COL|COLOMBIA|CR|COSTA RICA|MX|MEX|M[EÉ]XICO|SV|EL SALVADOR|PR|PUERTO RICO|UR|URU|URUGUAY|BOL|BOLIVIA|GT|GUATEMALA|HN|HON|HONDURAS|USA|US|EEUU|ITA|ITALIA|UK|CAN|CANAD[AÁ]|PT|PORTUGAL|PY|PARAGUAY|ES|ESP|ESPA[ÑN]A|PANAMA|BR|BRA|BRASIL|EC|ECU|ECUADOR|VE|VEN|VZL|VENEZUELA|DO|DOM|RD|R\s?DOM|REP\s?DOMINICANA|NI|NIC|NICARAGUA|CU|CUB|CUBA)\b"
    
    match = re.search(pattern, text, flags=re.IGNORECASE)
    
    if match:
        raw_country = match.group(1).upper()
        normalized = ''.join(c for c in unicodedata.normalize('NFD', raw_country) if unicodedata.category(c) != 'Mn')
        return COUNTRY_MAP.get(normalized)
        
    return None

def clean_suffixes_and_noise(text: str) -> str:
    
    text = re.sub(r'(?i)\b(OPCION|OPC|OP|OPT)\s*#?\s*\d+\b', '', text)
    
    text = re.sub(r'\((SOLO EVENTOS[^)]*|EXCLUSIVO|OFFLINE|PP|I|OPC[^)]*)\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(SOLO EVENTOS|EXCLUSIVO|OFFLINE)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?i)\bVIP\s*MOVIE\s*(?:\d+)?\b', '', text)
    
    country_pattern = r"\b(CL|CHI|CHILE|CH|PE|PER[UÚ]|PER|AR|ARG|ARGENTINA|CO|COL|COLOMBIA|CR|COSTA RICA|MX|MEX|M[EÉ]XICO|SV|EL SALVADOR|PR|PUERTO RICO|UR|URU|URUGUAY|BOL|BOLIVIA|GT|GUATEMALA|HN|HON|HONDURAS|USA|US|EEUU|ITA|ITALIA|UK|CAN|CANAD[AÁ]|PT|PORTUGAL|PY|PARAGUAY|ES|ESP|ESPA[ÑN]A|PANAMA|BR|BRA|BRASIL|EC|ECU|ECUADOR|VE|VEN|VZL|VENEZUELA|DO|DOM|RD|R\s?DOM|REP\s?DOMINICANA|NI|NIC|NICARAGUA|CU|CUB|CUBA|SUR|LAT|LATINO)\b"
    
    text = re.sub(rf'\(\s*{country_pattern}\s*\)', '', text, flags=re.IGNORECASE)
    
    if not re.search(r'(?i)\bvs\b', text):
        text = re.sub(country_pattern, '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\(\s+', '(', text) 
    text = re.sub(r'\s+\)', ')', text) 
    text = re.sub(r'\(\)', '', text)  
    text = re.sub(r'(?i)\b24\s*7\b', '24/7', text) 
    
    text = re.sub(r'\bF\b\s*$', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'(?<!\d)/(?!\d)', ' ', text)
    
    text = re.sub(r'[\-\s|/:]+$', '', text)

    text = re.sub(r'(?<=\D)-(?=\d)', ' ', text)
    
    return text


def clean_category_name(text: str) -> str:
    if not text:
        return "SIN CLASIFICAR"
    
    text = remove_emojis(text)
        
    text = re.sub(r'(?i)\bE?[\$€]?[ŠS]PN\b', 'ESPN', text)
    text = re.sub(r'(?i)5PORT5', 'SPORTS', text)
    text = re.sub(r'(?i)D[3E]P[OÖØ0]RT[E3]S', 'DEPORTES', text)
    
    leet_map = {'$': 'S', 'Š': 'S', 'Ə': 'E', '€': 'E', 'Ö': 'O', 'Ø': 'O', '⚽': 'O', '@': 'A', 'Æ': 'A', 'Ï': 'I'}
    for bad, good in leet_map.items():
        text = text.replace(bad, good)
        
    text = text.replace('_', ' ')
    
    return text.strip()