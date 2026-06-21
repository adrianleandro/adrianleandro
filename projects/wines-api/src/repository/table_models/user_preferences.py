from sqlalchemy import select, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.repository.config.table import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    user_id = Column(ForeignKey("users.uid"))
    option_id = Column(ForeignKey("preference_options.id"))
    weight = Column(Integer, nullable=False, default=1)
    user = relationship("User", back_populates="preferences")