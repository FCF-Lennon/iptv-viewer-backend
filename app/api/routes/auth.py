from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token
from app.core.security import hasH_password, verify_password, create_access_token
from app.core.config import setting  # <-- usamos setting para decidir entorno
from app.schemas.xtream import XtreamCredentials
from app.core.security import get_current_user
from app.core.xtream_store import user_xtream_credentials

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


# Login / token según entorno
if setting.app_env == "development":
    # Solo para Swagger/dev: /auth/token con OAuth2PasswordRequestForm
    @router.post("/token", response_model=Token)
    def login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        db_user = db.query(User).filter(User.email == form_data.username).first()
        if not db_user or not verify_password(form_data.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        token = create_access_token({"sub": db_user.email})
        return {"access_token": token, "token_type": "bearer"}

else:
    # Producción/frontend: /auth/login con JSON
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
    email: str = Depends(get_current_user)
):
    user_xtream_credentials[email] = creds
    return {"message": "Credenciales guardadas"}