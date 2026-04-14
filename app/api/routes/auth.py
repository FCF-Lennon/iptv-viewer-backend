from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.xtream_credentials import XtreamCredentials as XtreamModel
from app.schemas.xtream import XtreamCredentials
from app.schemas.auth import UserCreate, UserLogin, Token
from app.core.security import hasH_password, verify_password, create_access_token
from app.core.config import setting  
from app.core.security import get_current_user, encrypt_password
from app.db.session import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Registro de usuario
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_user = User(
        email=user.email,
        hashed_password=hasH_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario creado correctamente"}

@router.post("/token", response_model=Token)
def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/xtream")
def set_xtream_credentials(
    creds: XtreamCredentials,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # limitar máximo 5
    count = db.query(XtreamModel)\
        .filter(XtreamModel.user_id == user.id)\
        .count()

    if count >= 5:
        raise HTTPException(
            status_code=400,
            detail="Máximo de 5 credenciales alcanzado"
        )

    # si será activa, desactivar las demás
    if creds.is_active:
        db.query(XtreamModel)\
            .filter(XtreamModel.user_id == user.id)\
            .update({"is_active": False})
        db.commit()

    encrypted = encrypt_password(creds.password)

    new_credentials = XtreamModel(
        user_id=user.id,
        name=creds.name,
        host=creds.host,
        username=creds.username,
        password_encrypted=encrypted,
        is_active=creds.is_active
    )

    db.add(new_credentials)
    db.commit()
    db.refresh(new_credentials)

    return {"message": "Credenciales guardadas"}

@router.get("/xtream")
def get_xtream_credentials(
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    creds = db.query(XtreamModel)\
        .filter(XtreamModel.user_id == user.id)\
        .all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "host": c.host,
            "username": c.username,
            "is_active": c.is_active,
            "created_at": c.created_at
        }
        for c in creds
    ]


@router.patch("/xtream/{cred_id}/activate")
def activate_xtream(
    cred_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cred = db.query(XtreamModel)\
        .filter(
            XtreamModel.id == cred_id,
            XtreamModel.user_id == user.id
        ).first()

    if not cred:
        raise HTTPException(status_code=404, detail="Credencial no encontrada")

    # desactivar todas
    db.query(XtreamModel)\
        .filter(XtreamModel.user_id == user.id)\
        .update({"is_active": False})
    db.commit()

    # activar esta
    cred.is_active = True
    db.commit()

    return {"message": "Credencial activada"}


@router.delete("/xtream/{cred_id}")
def delete_xtream(
    cred_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.email == email).first()

    cred = db.query(XtreamModel)\
        .filter(
            XtreamModel.id == cred_id,
            XtreamModel.user_id == user.id
        ).first()

    if not cred:
        raise HTTPException(status_code=404, detail="Credencial no encontrada")

    db.delete(cred)
    db.commit()

    return {"message": "Credencial eliminada"}