from sqlalchemy import Column, Integer, String
from app.db.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    xtream_credentials = relationship(
        "XtreamCredentials", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    favorites = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

