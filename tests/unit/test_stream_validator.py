import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
import app.services.stream_validator as stream_validator

@pytest.fixture(autouse=True)
def clear_cache():
    """
    Limpia estado global antes de cada test.
    """
    stream_validator._stream_cache.clear()
    stream_validator._pending_revalidations.clear()
    yield
    stream_validator._stream_cache.clear()
    stream_validator._pending_revalidations.clear()


@pytest.mark.asyncio
async def test_validate_stream_cache_miss_calls_check_vod(monkeypatch):
    mock_check = AsyncMock(return_value=True)
    monkeypatch.setattr(
        stream_validator,
        "_check_vod",
        mock_check
    )

    result = await stream_validator.validate_stream(
        "movie",
        1,
        "http://fake-url"
    )

    assert result is True
    assert mock_check.await_count == 1


@pytest.mark.asyncio
async def test_validate_stream_cache_hit_does_not_call_check_vod(monkeypatch):
    mock_check = AsyncMock(return_value=True)
    monkeypatch.setattr(
        stream_validator,
        "_check_vod",
        mock_check
    )

    # Primera llamada → cache miss
    result1 = await stream_validator.validate_stream(
        "movie",
        1,
        "http://fake-url"
    )

    # Segunda llamada → cache hit
    result2 = await stream_validator.validate_stream(
        "movie",
        1,
        "http://fake-url"
    )

    assert result1 is True
    assert result2 is True
    assert mock_check.await_count == 1  # 🔥 solo se ejecutó una vez


""" 
Qué validamos aquí?:

- Que en cache miss se ejecuta _check_vod
- Que en cache hit NO vuelve a ejecutarse
- Que el valor almacenado se reutiliza
- Que no tocamos httpx real 
"""

@pytest.mark.asyncio
async def test_validate_stream_cache_miss_calls_check_vod_and_caches_result():

    # Limpiar cache antes del test
    stream_validator._stream_cache.clear()

    with patch.object(
        stream_validator,
        "_check_vod",
        return_value=True
    ) as mock_check_vod:

        result = await stream_validator.validate_stream(
            stream_type="vod",
            stream_id="123",
            url="http://fake-url"
        )

        # 1️⃣ Debe retornar True
        assert result is True

        # 2️⃣ Debe haber llamado al validador real
        mock_check_vod.assert_called_once()

        # 3️⃣ Debe haberse guardado en cache
        assert "vod:123" in stream_validator._stream_cache

""" 
Qué estamos verificando exactamente?:

✔ Cuando no hay cache
✔ Se llama al validador interno
✔ Se guarda en _stream_cache
✔ Retorna correctamente 
"""

@pytest.mark.asyncio
async def test_concurrent_requests_only_trigger_one_validation():

    stream_validator._stream_cache.clear()
    stream_validator._pending_revalidations.clear()

    async def fake_check_vod(*args, **kwargs):
        await asyncio.sleep(0.1)
        return True

    with patch.object(
        stream_validator,
        "_check_vod",
        side_effect=fake_check_vod
    ) as mock_check_vod:

        await asyncio.gather(
            stream_validator.validate_stream("vod", "999", "http://fake"),
            stream_validator.validate_stream("vod", "999", "http://fake")
        )

        # Solo debe ejecutarse una vez
        assert mock_check_vod.call_count == 1


""" 
Qué valida esto?:

✔ _pending_revalidations evita doble validación
✔ No hay race condition
✔ No se dispara doble request real
✔ Xtream no se toca dos veces 
"""

@pytest.mark.asyncio
async def test_ttl_expired_triggers_background_revalidation():

    stream_validator._stream_cache.clear()
    stream_validator._pending_revalidations.clear()

    key = "movie:555"

    # Simular cache vencido
    stream_validator._stream_cache[key] = {
        "valid": True,
        "checked_at": time.time() - 999999  # Muy viejo
    }

    with patch.object(
        stream_validator,
        "_background_revalidate"
    ) as mock_background:

        result = await stream_validator.validate_stream(
            "movie",
            555,
            "http://fake"
        )

        # 1️⃣ Debe retornar valor viejo
        assert result is True

        # 2️⃣ Debe lanzar revalidación en background
        mock_background.assert_called_once()


""" 
Qué estamos validando?:

✔ No bloquea request
✔ Devuelve stale value
✔ Dispara revalidación async
✔ No hace validación síncrona 
"""