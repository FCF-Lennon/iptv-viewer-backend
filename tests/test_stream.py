import pytest
from app.services.xtream_service import XtreamClient
from typing import Optional

@pytest.mark.asyncio
async def test_movies_api():
    client = XtreamClient(host="http://example.com", username="user", password="pass")
    movies = await client.get_movies()
    await client.close()
    
    print("Películas recibidas:", movies)
    assert movies is not None
    assert isinstance(movies, list)

