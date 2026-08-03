from sqlalchemy.orm import Session
from app.models.xtream_credentials import XtreamCredentials
from app.models.user import User
from app.core.security import decrypt_password

def get_active_xtream_credentials(db: Session, user_id: int):

    creds = db.query(XtreamCredentials)\
        .filter(
            XtreamCredentials.user_id == user_id,
            XtreamCredentials.is_active == True
        ).first()
    
    if not creds:
        return None
    
    return {
        "host": creds.host, 
        "username": creds.username,
        "password": decrypt_password(creds.password_encrypted)
    }


def get_active_xtream_credentials_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    return get_active_xtream_credentials(db, user.id)