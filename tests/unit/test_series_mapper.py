import pytest
from unittest.mock import AsyncMock
from app.services.mappers.series_mapper import normalize_series, normalize_series_detail
from app.services.xtream_service import XtreamClient

def test_series_mapper_basic():

    raw = {
        "series_id": 10,
        "name": " Breaking Bad 2008 ",
        "cover": "poster.jpg",
        "category_id": "3",
        "rating": "9.5"
    }

    result = normalize_series(raw)

    assert result.id == 10
    assert result.title == "Breaking Bad"
    assert result.year == 2008
    assert result.poster == "poster.jpg"
    assert result.category == "3"
    assert result.rating == 9.5
    assert result.type == "series"


"""
Qué estamos validando?:

✔ limpieza del título (espacios + año)
✔ extracción correcta del año
✔ conversión de rating a float
✔ preservación de category_id
✔ estructura base válida del schema
"""

def test_series_detail_seasons_and_episodes_sorted():

    raw = {
        "info": {"name": "Test Series"},
        "seasons": [
            {"season_number": 2},
            {"season_number": 1}
        ],
        "episodes": {
            "1": [
                {"id": 1, "episode_num": 2, "title": "Ep 2"},
                {"id": 2, "episode_num": 1, "title": "Ep 1"}
            ],
            "2": [
                {"id": 3, "episode_num": 1, "title": "Ep A"}
            ]
        }
    }

    result = normalize_series_detail(raw, 10)

    seasons = result["seasons"]

    assert seasons[0]["season_number"] == 1
    assert seasons[1]["season_number"] == 2

    assert seasons[0]["episodes"][0]["episode_num"] == 1
    assert seasons[0]["episodes"][1]["episode_num"] == 2


"""
Qué estamos validando?:

✔ orden correcto de temporadas
✔ orden correcto de episodios dentro de cada temporada
✔ estructura consistente de seasons → episodes
✔ protección contra desorden típico de Xtream
"""

def test_series_detail_episode_title_cleanup():

    raw = {
        "info": {"name": "Test"},
        "seasons": [{"season_number": 1}],
        "episodes": {
            "1": [
                {"id": 1, "episode_num": 1, "title": "🔥 Pilot 🔥"}
            ]
        }
    }

    result = normalize_series_detail(raw, 1)

    title = result["seasons"][0]["episodes"][0]["title"]

    assert title == "Pilot"


"""
Qué estamos validando?:

✔ eliminación de emojis en títulos de episodios
✔ normalización de texto IPTV corrupto
✔ consistencia con text_cleaner
"""

def test_series_detail_empty_seasons():

    raw = {
        "info": {"name": "Empty Series"},
        "seasons": [],
        "episodes": {}
    }

    result = normalize_series_detail(raw, 99)

    assert result["seasons"] == []
    assert result["total_seasons"] == 0
    assert result["total_episodes"] == 0


"""
Qué estamos validando?:

✔ manejo de series sin temporadas
✔ no rompe con datos vacíos
✔ contadores correctos en cero
✔ respuesta válida para frontend
"""


def test_series_detail_total_episodes_count():

    raw = {
        "info": {"name": "Test"},
        "seasons": [{"season_number": 1}],
        "episodes": {
            "1": [
                {"id": 1, "episode_num": 1},
                {"id": 2, "episode_num": 2}
            ]
        }
    }

    result = normalize_series_detail(raw, 1)

    assert result["total_episodes"] == 2


"""
Qué estamos validando?:

✔ conteo correcto de episodios
✔ acumulación por temporada
✔ integridad de métricas para frontend
"""

@pytest.mark.asyncio
async def test_series_categories_basic():

    client = XtreamClient()

    client._get = AsyncMock(return_value=[
        {"category_id": "1", "category_name": "🔥 Acción 🔥"}
    ])

    result = await client.get_series_categories()

    assert result[0].category_id == "1"
    assert result[0].category_name == "Acción"


"""
Qué estamos validando?:

✔ limpieza de emojis en categorías
✔ normalización de texto
✔ mapeo correcto de category_id
✔ estructura de salida consistente
"""

@pytest.mark.asyncio
async def test_series_categories_invalid_data():

    client = XtreamClient()

    client._get = AsyncMock(return_value=[
        None,
        "invalid",
        {"category_id": "2", "category_name": "Drama"}
    ])

    result = await client.get_series_categories()

    assert len(result) == 1
    assert result[0].category_name == "Drama"


"""
Qué estamos validando?:

✔ ignora datos inválidos
✔ robustez frente a respuestas corruptas de Xtream
✔ no rompe el flujo
"""


@pytest.mark.asyncio
async def test_series_categories_empty():

    client = XtreamClient()

    client._get = AsyncMock(return_value=[])

    result = await client.get_series_categories()

    assert result == []


"""
Qué estamos validando?:

✔ manejo de listas vacías
✔ respuesta consistente
✔ no rompe el cliente
"""