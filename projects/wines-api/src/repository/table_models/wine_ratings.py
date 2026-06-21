from sqlalchemy import select, Column, String, Float, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from src.repository.config.table import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.repository.table_models.wines import Wine
from src.repository.table_models.user import User


class WineRating(Base):
    __tablename__ = 'wine_ratings'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False
    )
    wine_id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )
    review = Column(String, nullable=True)

    def __init__(self, wine_id: int, rating: float, user_id: str, review: str):
        self.wine_id = wine_id
        self.rating = rating
        self.user_id = user_id
        self.date = func.timezone('UTC-3', func.now())
        self.review = review