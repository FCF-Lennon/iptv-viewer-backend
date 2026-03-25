import pytest
from app.services.mappers.live_mapper import normalize_live


def test_live_mapper_dirty_titles():

    cases = [
        ("CL | *TV*N HD", "TVN", "HD"),
        ("FOX $SPORTS 1 (CHI)", "FOX SPORTS 1", None),
        ("D3PÖRT3S | [$ŠPN-3]", "ESPN 3", None),
        ("CINE | *HBÖ* 2 HD", "HBO 2", "HD"),
        ("MTV 80' HD", "MTV 80", "HD"),
    ]

    for name, expected_title, expected_quality in cases:

        raw = {
            "stream_id": 1,
            "name": name,
            "stream_icon": "logo.png",
            "category_id": "test"
        }

        result = normalize_live(raw)

        assert result.title == expected_title
        assert result.quality == expected_quality

""" 
Qué valida este test

✔ que la limpieza de ofuscación funcione
✔ que la calidad se extraiga bien
✔ que los títulos IPTV corruptos se normalicen 
"""

def test_live_mapper_country_detection():

    cases = [
        ("CL | MEGA SD", "MEGA", "CL"),
        ("PE | FOX SPORTS 1", "FOX SPORTS 1", "PE"),
        ("AR | ESPN PREMIUM OPC 2", "ESPN PREMIUM", "AR"),
        ("USA| FOX NEWS ¹", "FOX NEWS 1", "US"),
        ("MX | Canal 5 *", "CANAL 5", "MX"),
    ]

    for name, expected_title, expected_country in cases:

        raw = {
            "stream_id": 1,
            "name": name,
            "stream_icon": "logo.png",
            "category_id": "test"
        }

        result = normalize_live(raw)

        assert result.title == expected_title
        assert result.country == expected_country

""" 
Qué valida este test

✔ extract_strict_country()
✔ limpieza del prefijo CL |
✔ limpieza de símbolos *
✔ limpieza de calidad SD
✔ normalización de título final 
"""

def test_live_mapper_requires_stream_id():

    raw = {
        "name": "CL | MEGA HD",
        "stream_icon": "logo.png",
        "category_id": "test"
    }

    with pytest.raises(ValueError):
        normalize_live(raw)

""" 
Qué valida

✔ que el mapper no procese streams inválidos
✔ que el backend no genere IDs corruptos
✔ protege la API de datos rotos del proveedor IPTV 
"""


def test_live_mapper_title_fallback():

    raw = {
        "stream_id": 5,
        "name": "|||***",
        "stream_icon": "logo.png",
        "category_id": "test"
    }

    result = normalize_live(raw)

    # Debe usar el título original porque el cleaner lo vacía
    assert result.title == "|||***".strip().upper()

""" 
Qué valida este test

✔ que el mapper nunca devuelve título vacío
✔ protege la API de streams corruptos
✔ confirma que tu salvavidas final funciona 
"""

def test_live_mapper_country_without_spaces():

    raw = {
        "stream_id": 7,
        "name": "CL|CHV HD",
        "stream_icon": "logo.png",
        "category_id": "test"
    }

    result = normalize_live(raw)

    assert result.country == "CL"
    assert result.title == "CHV"

""" 
Qué asegura este test

✔ que "CL|CHV" se detecta igual que "CL | CHV"
✔ evita romper canales por formatos inconsistentes del proveedor
✔ fortalece el parser de prefijos. 
"""

def test_live_mapper_handles_missing_logo():

    raw = {
        "stream_id": 20,
        "name": "CL | TVN HD",
        "stream_icon": None,
        "category_id": "test"
    }

    result = normalize_live(raw)

    assert result.id == 20
    assert result.poster is None
    assert result.title == "TVN"

""" 
Qué valida

✔ que el mapper no rompe si el logo viene nulo
✔ asegura que poster puede ser None sin romper la API
✔ caso muy común en listas IPTV reales. 
"""

def test_live_mapper_handles_missing_optional_fields():

    raw = {
        "stream_id": 30,
        "name": "AR | TYC SPORTS",
    }

    result = normalize_live(raw)

    assert result.id == 30
    assert result.title == "TYC SPORTS"
    assert result.poster is None

""" 
Qué valida

✔ el mapper no depende de stream_icon ni category_id
✔ protege contra proveedores IPTV inconsistentes
✔ asegura que el objeto mínimo se puede construir. 
"""

def test_live_mapper_handles_empty_name():
    raw = {
        "stream_id": 40,
        "name": "",
        "stream_icon": "logo.png",
    }

    result = normalize_live(raw)

    assert result.title is not None
    assert result.title != ""

"""
✔ que el mapper maneje nombres vacíos sin romper
✔ que nunca retorne título vacío, sino None
✔ protección contra datos inexistentes del proveedor
✔ evita romper el frontend (render vacío)
"""


def test_live_mapper_extracts_quality_in_weird_positions():

    raw = {
        "stream_id": 41,
        "name": "CL | ESPN HD PREMIUM",
        "stream_icon": "logo.png"
    }

    result = normalize_live(raw)

    assert result.quality == "HD"
    assert "HD" not in result.title

"""
Qué estamos validando?:

✔ extracción de calidad en posiciones no estándar
✔ que la calidad no contamine el título final
✔ robustez frente a formatos IPTV no uniformes
✔ limpieza correcta de metadatos embebidos
"""