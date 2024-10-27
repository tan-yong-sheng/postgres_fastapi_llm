import datetime

import passlib.hash
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.schema import CheckConstraint, UniqueConstraint
from sqlalchemy.types import TEXT, DateTime, Integer, String

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


class SessionOrm(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="cascade", name="fk__session__user_id"),
        nullable=False,
    )
    start_timestamp = Column(
        DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)
    )
    end_timestamp = Column(DateTime(timezone=True), nullable=True, default=None)


class MessageOrm(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="cascade", name="fk__message__user_id"),
        nullable=False,
    )
    session_id = Column(
        Integer,
        ForeignKey("session.id", ondelete="cascade", name="fk__message__session_id"),
        nullable=False,
    )
    role = Column(String, nullable=False)
    content = Column(TEXT, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)

    __tableargs__ = {
        CheckConstraint("LENGTH(content)>0", name="check__message__content_length"),
    }
