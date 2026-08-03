import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user
from app.db.session import get_db

# ---------------------------------------------------------------------------
# Setup: DB en memoria con SQLite para tests
# ---------------------------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.favorite import Favorite
from app.models.xtream_credentials import XtreamCredentials  # necesario para create_all

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Crear usuario de prueba en la DB de testing
def setup_test_user(db):
    user = db.query(User).filter(User.email == "test@test.com").first()
    if not user:
        user = User(email="test@test.com", hashed_password="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: "test@test.com"
    yield
    app.dependency_overrides.clear()

# Asegurar que el usuario de prueba existe
with TestingSessionLocal() as db:
    setup_test_user(db)

client = TestClient(app)


# ---------------------------------------------------------------------------
# Tests: GET /favorites/
# ---------------------------------------------------------------------------

def test_list_favorites_empty():
    """Lista vacía cuando no hay favoritos."""
    response = client.get("/favorites/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_favorites_returns_only_own():
    """Cada usuario solo ve sus propios favoritos."""
    db = TestingSessionLocal()
    user = setup_test_user(db)

    # Limpiar y crear favorito
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    db.add(Favorite(user_id=user.id, content_type="movie", content_id=1, name="Test Movie"))
    db.commit()
    db.close()

    response = client.get("/favorites/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Movie"
    assert data[0]["content_type"] == "movie"

    # Limpiar
    db = TestingSessionLocal()
    user = setup_test_user(db)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Tests: POST /favorites/
# ---------------------------------------------------------------------------

def test_add_favorite_success():
    """Agregar favorito devuelve 201 con los datos correctos."""
    db = TestingSessionLocal()
    user = setup_test_user(db)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    db.commit()
    db.close()

    response = client.post("/favorites/", json={
        "content_type": "movie",
        "content_id": 42,
        "name": "Inception"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["content_id"] == 42
    assert data["name"] == "Inception"
    assert data["content_type"] == "movie"
    assert "id" in data

    # Limpiar
    db = TestingSessionLocal()
    user = setup_test_user(db)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    db.commit()
    db.close()


def test_add_favorite_duplicate_returns_409():
    """Agregar el mismo contenido dos veces devuelve 409."""
    db = TestingSessionLocal()
    user = setup_test_user(db)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    db.commit()
    db.close()

    payload = {"content_type": "series", "content_id": 99, "name": "Breaking Bad"}

    r1 = client.post("/favorites/", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/favorites/", json=payload)
    assert r2.status_code == 409
    assert "ya está en tus favoritos" in r2.json()["detail"]

    # Limpiar
    db = TestingSessionLocal()
    user = setup_test_user(db)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    db.commit()
    db.close()


def test_add_favorite_invalid_content_type():
    """content_type inválido devuelve 422."""
    response = client.post("/favorites/", json={
        "content_type": "podcast",   # no permitido
        "content_id": 1,
        "name": "Algo"
    })
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests: DELETE /favorites/{id}
# ---------------------------------------------------------------------------

def test_remove_favorite_success():
    """Eliminar favorito propio devuelve 204."""
    db = TestingSessionLocal()
    user = setup_test_user(db)
    db.query(Favorite).filter(Favorite.user_id == user.id).delete()
    fav = Favorite(user_id=user.id, content_type="live", content_id=7, name="CNN")
    db.add(fav)
    db.commit()
    db.refresh(fav)
    fav_id = fav.id
    db.close()

    response = client.delete(f"/favorites/{fav_id}")
    assert response.status_code == 204

    # Verificar que fue eliminado
    db = TestingSessionLocal()
    assert db.query(Favorite).filter(Favorite.id == fav_id).first() is None
    db.close()


def test_remove_favorite_not_found():
    """Eliminar favorito inexistente devuelve 404."""
    response = client.delete("/favorites/99999")
    assert response.status_code == 404
