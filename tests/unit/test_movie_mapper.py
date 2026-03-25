import pytest
from app.services.mappers.movie_mapper import normalize_movie

def test_movie_mapper_basic_normalization():

    raw_movie = {
        "stream_id": 101,
        "name": " Avatar 2009 ",
        "stream_icon": "http://poster.jpg",
        "category_id": "5",
        "rating": "7.8"
    }

    result = normalize_movie(raw_movie)

    assert result.id == 101
    assert result.title == "Avatar"
    assert result.year == 2009
    assert result.poster == "http://poster.jpg"
    assert result.category == "5"
    assert result.rating == 7.8
    assert result.type == "movie"


""" 
Qué valida este test

✔ que stream_id se convierta correctamente a id
✔ que el título se limpie correctamente (" Avatar 2009 " → "Avatar")
✔ que el año se extraiga correctamente del título
✔ que el poster se preserve desde stream_icon
✔ que la category_id se mantenga en el mapper
✔ que rating se convierta correctamente a float
✔ que el tipo de contenido se establezca como "movie"
"""

def test_movie_mapper_requires_stream_id():

    raw_movie = {
        "name": "Inception 2010"
    }

    with pytest.raises(ValueError):
        normalize_movie(raw_movie)

""" 
Qué valida este test

✔ que stream_id sea obligatorio para normalizar una película
✔ que el mapper lance ValueError cuando el dato viene incompleto desde Xtream
✔ que el sistema no genere objetos inválidos sin identificador
✔ que se detecten datos corruptos o incompletos del proveedor IPTV antes de llegar a la API
"""

def test_movie_mapper_removes_emojis():
    raw_movie = {
        "stream_id": 55, 
        "name": "🔥 Joker 2019 🔥"
    }

    result = normalize_movie(raw_movie)

    assert result.title == "Joker"
    assert result.year == 2019

""" 
Qué valida este test

✔ que el mapper elimine emojis del título provenientes de listas IPTV
✔ que el título se normalice correctamente ("🔥 Joker 2019 🔥" → "Joker")
✔ que el año se extraiga correctamente incluso cuando el texto contiene caracteres extraños
✔ que la limpieza de texto no afecte la detección del año
"""

def test_movie_mapper_invalid_rating():
    raw_movie = {
        "stream_id": 77,
        "name": "Matrix 1999",
        "rating": "not-a-number"
    }

    result = normalize_movie(raw_movie)

    assert result.rating is None

""" 
Qué valida este test

✔ que el mapper maneje ratings inválidos provenientes de Xtream
✔ que safe_float no lance errores cuando el valor no es numérico
✔ que valores corruptos como "not-a-number" se conviertan en None
✔ que el sistema siga funcionando aunque el proveedor envíe datos inconsistentes
"""

def test_movie_mapper_handles_missing_poster():
    raw_movie = {
        "stream_id": 88,
        "name": "Interstellar 2014"
    }

    result = normalize_movie(raw_movie)

    assert result.poster is None

""" 
Qué valida este test

✔ que el mapper tolere la ausencia de stream_icon en los datos de Xtream
✔ que el campo poster sea opcional y se establezca como None si no existe
✔ que la normalización no falle cuando faltan metadatos no críticos
✔ que el sistema siga generando un ContentItemSchema válido aunque el proveedor no envíe imagen
"""

def test_movie_mapper_preserves_category():
    raw_movie = {
        "stream_id": 200,
        "name": "Gladiator 2000",
        "category_id": "12"
    }

    result = normalize_movie(raw_movie)

    assert result.category == "12"

"""
  Qué valida este test

✔ que el mapper preserve correctamente category_id recibido desde Xtream
✔ que la categoría no se modifique durante la normalización
✔ que el campo category del ContentItemSchema reciba el valor original
✔ que la relación entre contenido y categoría se mantenga intacta en la transformación de datos
"""

def test_movie_mapper_handles_missing_category():
    raw_movie = {
        "stream_id": 201,
        "name": "Titanic 1997"
    }

    result = normalize_movie(raw_movie)

    assert result.category is None

"""
  Qué valida este test

✔ que el mapper tolere la ausencia de category_id en los datos provenientes de Xtream
✔ que el campo category sea opcional y se establezca como None si no existe
✔ que la normalización no falle cuando faltan metadatos no críticos
✔ que el ContentItemSchema siga siendo válido aunque la película no tenga categoría asignada
"""

def test_movie_mapper_without_year():

    raw_movie = {
        "stream_id": 90,
        "name": "The Dark Knight"
    }

    result = normalize_movie(raw_movie)

    assert result.title == "The Dark Knight"
    assert result.year is None

""" 
Qué valida este test

✔ que el mapper funcione correctamente cuando el título no contiene año
✔ que extract_year() devuelva None si no encuentra un año válido
✔ que el título no se modifique innecesariamente cuando no hay año que remover
✔ que el ContentItemSchema permanezca válido aun sin metadatos de año
"""

def test_movie_mapper_whitespace_cleanup():

    raw_movie = {
        "stream_id": 91,
        "name": "   Gladiator     2000   "
    }

    result = normalize_movie(raw_movie)

    assert result.title == "Gladiator"
    assert result.year == 2000

"""
Qué valida este test

✔ que el mapper elimine espacios excesivos al inicio, medio y final del título
✔ que normalize_whitespace() normalice correctamente cadenas con espacios irregulares
✔ que la limpieza del texto no afecte la extracción correcta del año
✔ que títulos provenientes de listas IPTV se normalicen a un formato limpio y consistente
"""
