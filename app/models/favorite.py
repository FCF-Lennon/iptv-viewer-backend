from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, index=True)
    content_id = Column(Integer, index=True)
    name = Column(String)
