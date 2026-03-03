import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch


from app.main import app
from app.core.security import get_current_user

# Override autenticación
app.dependency_overrides[get_current_user] = lambda: "test_user"

client = TestClient(app)


# =====================================================
# MOVIES
# =====================================================

@patch("app.api.routes.movies.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.movies.XtreamClient")
def test_movie_play_success(mock_client_class, mock_validate):

    mock_validate.return_value = True

    mock_client = mock_client_class.return_value
    mock_client.get_movie_info = AsyncMock(return_value={
        "movie_data": {"container_extension": "mp4"}
    })
    mock_client.close = AsyncMock()

    response = client.get("/movies/1/play")

    assert response.status_code == 200
    assert "play_url" in response.json()


@patch("app.api.routes.movies.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.movies.XtreamClient")
def test_movie_play_not_found(mock_client_class, mock_validate):

    mock_client = mock_client_class.return_value
    mock_client.get_movie_info = AsyncMock(return_value={})
    mock_client.close = AsyncMock()

    response = client.get("/movies/999/play")

    assert response.status_code == 404


@patch("app.api.routes.movies.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.movies.XtreamClient")
def test_movie_stream_invalid(mock_client_class, mock_validate):

    mock_validate.return_value = False

    mock_client = mock_client_class.return_value
    mock_client.get_movie_info = AsyncMock(return_value={
        "movie_data": {"container_extension": "mp4"}
    })
    mock_client.close = AsyncMock()

    response = client.get("/movies/1/play")

    assert response.status_code == 404


# =====================================================
# SERIES
# =====================================================

@patch("app.api.routes.series.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.series.XtreamClient")
def test_series_play_success(mock_client_class, mock_validate):

    mock_validate.return_value = True

    mock_client = mock_client_class.return_value
    mock_client.get_series_info = AsyncMock(return_value={
        "episodes": {
            "1": [
                {"id": "10", "container_extension": "mp4"}
            ]
        }
    })
    mock_client.close = AsyncMock()

    response = client.get("/series/1/10/play")

    assert response.status_code == 200
    assert "play_url" in response.json()


@patch("app.api.routes.series.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.series.XtreamClient")
def test_series_episode_not_found(mock_client_class, mock_validate):

    mock_client = mock_client_class.return_value
    mock_client.get_series_info = AsyncMock(return_value={
        "episodes": {}
    })
    mock_client.close = AsyncMock()

    response = client.get("/series/1/10/play")

    assert response.status_code == 404


@patch("app.api.routes.series.validate_stream", new_callable=AsyncMock)
@patch("app.api.routes.series.XtreamClient")
def test_series_stream_invalid(mock_client_class, mock_validate):

    mock_validate.return_value = False

    mock_client = mock_client_class.return_value
    mock_client.get_series_info = AsyncMock(return_value={
        "episodes": {
            "1": [
                {"id": "10", "container_extension": "mp4"}
            ]
        }
    })
    mock_client.close = AsyncMock()

    response = client.get("/series/1/10/play")

    assert response.status_code == 404


# =====================================================
# LIVE
# =====================================================

@patch("app.api.routes.live.validate_stream", new_callable=AsyncMock)
def test_live_play_success(mock_validate):

    mock_validate.return_value = True

    response = client.get("/live/1/play")

    assert response.status_code == 200
    assert "play_url" in response.json()


@patch("app.api.routes.live.validate_stream", new_callable=AsyncMock)
def test_live_stream_invalid(mock_validate):

    mock_validate.return_value = False

    response = client.get("/live/1/play")

    assert response.status_code == 404