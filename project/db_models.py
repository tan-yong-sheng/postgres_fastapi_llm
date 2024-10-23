import datetime

from sqlalchemy import Column, Integer
from sqlalchemy.types import DateTime, String

from project.db_connection import Base


class UserOrm(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)
    )

    def password_verification(self, password: str):
        return self.password_hash == password
