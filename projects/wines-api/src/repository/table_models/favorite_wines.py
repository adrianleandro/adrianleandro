from sqlalchemy import select, Column, String, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.repository.config.table import Base
from sqlalchemy.sql import functions

class FavoriteWines(Base):
    __tablename__ = 'favorite_wines'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement='auto',
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )
    wine_id = Column(Integer, nullable=False)
    added_date = Column(DateTime(timezone=True), nullable=False, server_default=functions.now())

    def __init__(self, user_id: str, wine_id: int):
        self.wine_id = wine_id
        self.user_id = user_id