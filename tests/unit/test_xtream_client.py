import pytest
from app.services.xtream_service import XtreamClient

@pytest.mark.asyncio
async def test_get_success(monkeypatch):
    client = XtreamClient()

    class MockResponse:
        status_code = 200

        def json(self):
            return {"data": "ok"}

        def raise_for_status(self):
            pass

    async def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(client.client, "get", mock_get)

    result = await client._get("test_endpoint")

    assert result == {"data": "ok"}

"""
Qué estamos validando?:

✔ Request exitoso a Xtream
✔ Se parsea correctamente el JSON
✔ No rompe el flujo normal
"""

import httpx

@pytest.mark.asyncio
async def test_get_http_error(monkeypatch):
    client = XtreamClient()

    async def mock_get(*args, **kwargs):
        raise httpx.HTTPStatusError(
            "error",
            request=None,
            response=httpx.Response(500)
        )

    monkeypatch.setattr(client.client, "get", mock_get)

    result = await client._get("test")

    assert result is None

"""
Qué estamos validando?:

✔ Manejo de errores HTTP de Xtream
✔ No rompe el backend
✔ Retorna None ante fallo
"""

@pytest.mark.asyncio
async def test_get_timeout(monkeypatch):
    client = XtreamClient()

    async def mock_get(*args, **kwargs):
        raise httpx.RequestError("timeout")

    monkeypatch.setattr(client.client, "get", mock_get)

    result = await client._get("test")

    assert result is None


""" 
Qué estamos validando?:

✔ Manejo de timeout
✔ No bloquea request
✔ Backend resiliente 
"""

@pytest.mark.asyncio
async def test_get_invalid_json(monkeypatch):
    client = XtreamClient()

    class MockResponse:
        status_code = 200

        def json(self):
            raise ValueError()

        def raise_for_status(self):
            pass

    async def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(client.client, "get", mock_get)

    result = await client._get("test")

    assert result is None


""" 
Qué estamos validando?:

✔ Manejo de respuesta corrupta
✔ Protección contra datos inválidos
✔ No rompe el flujo normal
"""


@pytest.mark.asyncio
async def test_get_api_error_field(monkeypatch):
    client = XtreamClient()

    class MockResponse:
        status_code = 200

        def json(self):
            return {"error": "Invalid credentials"}

        def raise_for_status(self):
            pass

    async def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(client.client, "get", mock_get)

    result = await client._get("test")

    assert result is None


"""
Qué estamos validando?:

✔ Manejo de error lógico de Xtream (campo "error")
✔ No se considera respuesta válida aunque sea 200
✔ Protección contra credenciales inválidas o bloqueos
"""


@pytest.mark.asyncio
async def test_get_with_extra_params(monkeypatch):
    client = XtreamClient()

    captured_params = {}

    class MockResponse:
        status_code = 200

        def json(self):
            return {"ok": True}

        def raise_for_status(self):
            pass

    async def mock_get(url, params=None):
        nonlocal captured_params
        captured_params = params
        return MockResponse()

    monkeypatch.setattr(client.client, "get", mock_get)

    await client._get("test", {"category_id": "10"})

    assert captured_params["category_id"] == "10"


"""
Qué estamos validando?:

✔ Envío correcto de parámetros adicionales
✔ Integración con filtros de Xtream
✔ Soporte para category_id y futuras extensiones
"""


@pytest.mark.asyncio
async def test_get_empty_response(monkeypatch):
    client = XtreamClient()

    class MockResponse:
        status_code = 200

        def json(self):
            return {}

        def raise_for_status(self):
            pass

    async def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(client.client, "get", mock_get)

    result = await client._get("test")

    assert result == {}

"""
Qué estamos validando?:

✔ manejo de respuesta vacía pero válida
✔ No de considera error si Xtream responde {}
✔ Permite que capas superiores decidan cómo manejarlo
"""