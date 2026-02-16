import re

def remove_emojis(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"[^\w\s\-\|]", "", text)

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def extract_year(text: str):
    match = re.search(r"\((\d{4})\)", text)
    return int(match.group(1)) if match else None

def remove_year(text: str):
    return re.sub(r"\(\d{4}\)",  "", text)

def extract_quality(text: str):
    match = re.search(r"\b(HD|SD|FHD|4K|1080p|720p)\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else None

def extract_country(text: str):
    match = re.match(r"([A-Z]{2})\s\|", text)
    return match.group(1) if match else None

def clean_special_chars(text: str):
    text = remove_emojis(text)
    text = re.sub(r"[#]+", "", text)
    return text

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None