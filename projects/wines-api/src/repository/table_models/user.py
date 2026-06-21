import logging
from email.policy import default

from sqlalchemy import select, Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.repository.config.table import Base
from src.repository.table_models.user_preferences import UserPreference

class User(Base):
    __tablename__ = "users"

    uid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False
    )
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    onboarding_completed = Column(Boolean, nullable=False, default=False)
    preferences = relationship("UserPreference", back_populates="user")

    def uid_to_str(self):
        return str(self.uid)