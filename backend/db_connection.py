import logging
import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=True, bind=engine, class_=AsyncSession
)

Base = declarative_base()


async def get_db_session():
    async with SessionLocal() as db_session:
        try:
            yield db_session
        except Exception as e:
            await db_session.rollback()
            logger.error(f"Error: {e}")
            raise e


db_context = asynccontextmanager(get_db_session)
