import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv, find_dotenv

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

_ = load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(
    autocommit=False, autoflush=True, bind=engine, expire_on_commit=False
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
