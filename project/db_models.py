import datetime

import passlib.hash
from sqlalchemy import Column, Integer
from sqlalchemy.types import DateTime, String

from project.db_connection import Base


class UserOrm(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    user_role_id = Column(Integer)
    password_hash = Column(String)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def password_verification(self, password: str):
        return passlib.hash.bcrypt.verify(password, self.password_hash)
