from sqlalchemy import select, Column, String, Integer
from src.repository.config.table import Base

class PreferenceCategory(Base):
    __tablename__ = "preference_categories"

    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)