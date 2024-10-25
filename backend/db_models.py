import datetime

import passlib.hash
from sqlalchemy import Column, Integer
from sqlalchemy.sql.schema import CheckConstraint, UniqueConstraint
from sqlalchemy.types import DateTime, String

from backend.db_connection import Base


class UserOrm(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __tableargs__ = {
        UniqueConstraint("username", name="uq__user__username"),
        UniqueConstraint("email", name="uq__user__email"),
        CheckConstraint("LENGTH(username)>0", name="check__user__title_length"),
        CheckConstraint("LENGTH(email)>0", name="check__user__email_length"),
        CheckConstraint(
            "LENGTH(password_hash)>0", name="check__user__password_hash_length"
        ),
    }

    def password_verification(self, password: str):
        return passlib.hash.bcrypt.verify(password, self.password_hash)


if __name__ == "__main__":
    from backend.db_connection import engine

    Base.metadata.create_all(bind=engine)
