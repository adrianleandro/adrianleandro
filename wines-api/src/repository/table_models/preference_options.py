from sqlalchemy import select, Column, String, Integer, ForeignKey, Float
from sqlalchemy.sql import func
from src.repository.config.table import Base

class PreferenceOption(Base):
    __tablename__ = "preference_options"

    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    category_id = Column(ForeignKey("preference_categories.id"))
    option = Column(String, nullable=False)
    description = Column(String, nullable=True)
    value = Column(Float, nullable=True)