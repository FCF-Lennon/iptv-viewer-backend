from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import setting

engine = create_engine(
    setting.database_url, 
    echo=False, 
    connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

