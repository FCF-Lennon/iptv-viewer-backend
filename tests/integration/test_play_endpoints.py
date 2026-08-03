import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user
from app.db.session import get_db
from app.api.routes.stream import get_stream_user

# Override autenticación y DB
app.dependency_overrides[get_current_user] = lambda: "test_user"
app.dependency_overrides[get_stream_user] = lambda: "test_user"
app.dependency_overrides[get_db] = lambda: None

client = TestClient(app)

FAKE_CREDS = {
    "host": "http://example.com",
    "username": "user",
    "password": "pass",
}


# =====================================================
# HELPER: respuesta streaming falsa de httpx
# =====================================================

def _make_fake_streaming_response(status_code: int = 200):
    """Crea un mock de httpx.Response que soporta streaming async."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.headers = {
        "content-type": "video/mp4",
        "content-length": "1024",
    }

    async def fake_aiter_bytes(chunk_size=None):
        yield b"fake_video_bytes"

    mock_response.aiter_bytes = fake_aiter_bytes
    mock_response.aclose = AsyncMock()  # debe ser awaitable
    return mock_response


def _make_fake_http_client(fake_response):
    """Crea un mock de httpx.AsyncClient con send y aclose awaitable."""
    mock_client = MagicMock()
    mock_client.send = AsyncMock(return_value=fake_response)
    mock_client.aclose = AsyncMock()  # debe ser awaitable
    return mock_client


# =====================================================
# MOVIES — GET /stream/movie/{id}
# =====================================================

@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.stream.XtreamClient")
@patch("app.api.routes.stream.httpx.AsyncClient")
def test_movie_stream_success(mock_http_client, mock_xtream_class, mock_validate, mock_creds):
    """Stream de película responde 200 y retransmite bytes — sin exponer credenciales."""
    mock_validate.return_value = True

    # Mock del XtreamClient para obtener container_extension
    mock_xtream = mock_xtream_class.return_value
    mock_xtream.get_movie_info = AsyncMock(return_value={
        "movie_data": {"container_extension": "mp4"}
    })
    mock_xtream.close = AsyncMock()

    # Mock del cliente httpx para el proxy (send y aclose deben ser awaitable)
    fake_resp = _make_fake_streaming_response(200)
    mock_http_client.return_value = _make_fake_http_client(fake_resp)

    response = client.get("/stream/movie/1")

    assert response.status_code == 200
    # Verificar que las credenciales NO están en ningún header de respuesta
    for header_value in response.headers.values():
        assert "pass" not in header_value
        assert "user" not in header_value


@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.XtreamClient")
def test_movie_stream_not_found(mock_xtream_class, mock_creds):
    """Película inexistente devuelve 404."""
    mock_xtream = mock_xtream_class.return_value
    mock_xtream.get_movie_info = AsyncMock(return_value={})
    mock_xtream.close = AsyncMock()

    response = client.get("/stream/movie/999")

    assert response.status_code == 404


@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.stream.XtreamClient")
def test_movie_stream_invalid(mock_xtream_class, mock_validate, mock_creds):
    """Stream inválido devuelve 404 sin llegar a hacer proxy."""
    mock_validate.return_value = False

    mock_xtream = mock_xtream_class.return_value
    mock_xtream.get_movie_info = AsyncMock(return_value={
        "movie_data": {"container_extension": "mp4"}
    })
    mock_xtream.close = AsyncMock()

    response = client.get("/stream/movie/1")

    assert response.status_code == 404


@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=None)
def test_movie_stream_no_credentials(mock_creds):
    """Sin credenciales Xtream configuradas devuelve 400."""
    response = client.get("/stream/movie/1")
    assert response.status_code == 400


# =====================================================
# SERIES — GET /stream/series/{series_id}/{episode_id}
# =====================================================

@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.stream.XtreamClient")
@patch("app.api.routes.stream.httpx.AsyncClient")
def test_series_stream_success(mock_http_client, mock_xtream_class, mock_validate, mock_creds):
    """Stream de episodio responde 200 — sin exponer credenciales."""
    mock_validate.return_value = True

    mock_xtream = mock_xtream_class.return_value
    mock_xtream.get_series_info = AsyncMock(return_value={
        "episodes": {
            "1": [{"id": "10", "container_extension": "mp4"}]
        }
    })
    mock_xtream.close = AsyncMock()

    fake_resp = _make_fake_streaming_response(200)
    mock_http_client.return_value = _make_fake_http_client(fake_resp)

    response = client.get("/stream/series/1/10")

    assert response.status_code == 200
    for header_value in response.headers.values():
        assert "pass" not in header_value
        assert "user" not in header_value


@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.XtreamClient")
def test_series_episode_not_found(mock_xtream_class, mock_creds):
    """Episodio inexistente devuelve 404."""
    mock_xtream = mock_xtream_class.return_value
    mock_xtream.get_series_info = AsyncMock(return_value={"episodes": {}})
    mock_xtream.close = AsyncMock()

    response = client.get("/stream/series/1/10")
    assert response.status_code == 404


@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.stream.XtreamClient")
def test_series_stream_invalid(mock_xtream_class, mock_validate, mock_creds):
    """Stream inválido devuelve 404."""
    mock_validate.return_value = False

    mock_xtream = mock_xtream_class.return_value
    mock_xtream.get_series_info = AsyncMock(return_value={
        "episodes": {
            "1": [{"id": "10", "container_extension": "mp4"}]
        }
    })
    mock_xtream.close = AsyncMock()

    response = client.get("/stream/series/1/10")
    assert response.status_code == 404


# =====================================================
# LIVE TV — GET /stream/live/{id}
# =====================================================

@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.stream.httpx.AsyncClient")
def test_live_stream_success(mock_http_client, mock_validate, mock_creds):
    """Stream de canal en vivo responde 200 — sin exponer credenciales."""
    mock_validate.return_value = True

    fake_resp = _make_fake_streaming_response(200)
    mock_http_client.return_value = _make_fake_http_client(fake_resp)

    response = client.get("/stream/live/1")

    assert response.status_code == 200
    for header_value in response.headers.values():
        assert "pass" not in header_value
        assert "user" not in header_value


@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=FAKE_CREDS)
@patch("app.api.routes.stream.validate_stream", new_callable=AsyncMock)
def test_live_stream_invalid(mock_validate, mock_creds):
    """Stream inválido devuelve 404."""
    mock_validate.return_value = False

    response = client.get("/stream/live/1")
    assert response.status_code == 404


@patch("app.api.routes.stream.get_active_xtream_credentials_by_email", return_value=None)
def test_live_stream_no_credentials(mock_creds):
    """Sin credenciales Xtream configuradas devuelve 400."""
    response = client.get("/stream/live/1")
    assert response.status_code == 400


# =====================================================
# SEGURIDAD: verificar que los endpoints /play ya no existen
# =====================================================

def test_old_movie_play_endpoint_removed():
    """/movies/{id}/play ya no debe existir (eliminado)."""
    response = client.get("/movies/1/play")
    assert response.status_code == 404


def test_old_live_play_endpoint_removed():
    """/live/{id}/play ya no debe existir (eliminado)."""
    response = client.get("/live/1/play")
    assert response.status_code == 404


def test_old_series_play_endpoint_removed():
    """/series/{id}/{ep}/play ya no debe existir (eliminado)."""
    response = client.get("/series/1/10/play")
    assert response.status_code == 404