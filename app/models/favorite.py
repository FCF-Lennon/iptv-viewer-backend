from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    content_type = Column(String, nullable=False, index=True)  # movie | series | live
    content_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    # Evitar duplicados: un usuario no puede favoritear el mismo contenido dos veces
    __table_args__ = (
        UniqueConstraint("user_id", "content_type", "content_id", name="uq_user_content"),
    )

    user = relationship("User", back_populates="favorites")
