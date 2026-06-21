from supabase import create_client, Client
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from src.config.manager import settings


class Database:
    def __init__(self):
        self.postgres_uri = str(PostgresDsn(settings.DB_POSTGRES_URI))

        self.engine = create_engine(
            url=self.postgres_uri,
            poolclass=QueuePool,
        )

        self.sessionmaker = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )

db = Database()