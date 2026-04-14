from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import setting

if setting.database_url.startswith("sqlite"):
    engine = create_engine(
        setting.database_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        setting.database_url,
        echo=False
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()