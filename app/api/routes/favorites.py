from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.favorite import FavoriteCreate, FavoriteResponse

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"]
)


def _get_user(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/", response_model=List[FavoriteResponse])
def list_favorites(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos los favoritos del usuario autenticado."""
    user = _get_user(db, current_user)
    return db.query(Favorite).filter(Favorite.user_id == user.id).all()


@router.post("/", response_model=FavoriteResponse, status_code=201)
def add_favorite(
    payload: FavoriteCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Agrega un contenido a favoritos. Devuelve 409 si ya existe."""
    user = _get_user(db, current_user)

    favorite = Favorite(
        user_id=user.id,
        content_type=payload.content_type,
        content_id=payload.content_id,
        name=payload.name,
    )

    db.add(favorite)
    try:
        db.commit()
        db.refresh(favorite)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Este contenido ya está en tus favoritos"
        )

    return favorite


@router.delete("/{favorite_id}", status_code=204)
def remove_favorite(
    favorite_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina un favorito por ID. Solo puede eliminar los propios."""
    user = _get_user(db, current_user)

    favorite = db.query(Favorite).filter(
        Favorite.id == favorite_id,
        Favorite.user_id == user.id   # evita eliminar favoritos de otros usuarios
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")

    db.delete(favorite)
    db.commit()
