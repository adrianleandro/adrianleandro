from sqlalchemy import select, Column, String, Integer, Float
from src.repository.config.table import Base

class Wine(Base):
    __tablename__ = "wines"

    wine_id = Column(Integer, primary_key=True)
    wine_name = Column(String, nullable=True)
    type = Column(String, nullable=True)
    elaborate = Column(String, nullable=True)
    grapes = Column(String, nullable=True)
    harmonize = Column(String, nullable=True)
    abv = Column(Float, nullable=True)
    body = Column(String, nullable=True)
    acidity = Column(String, nullable=True)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    winery = Column(String, nullable=True)
    vintages = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    harmonize_es = Column(String, nullable=True)
