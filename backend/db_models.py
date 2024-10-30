import datetime

import passlib.hash
from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.sql.schema import CheckConstraint, UniqueConstraint
from sqlalchemy.types import TEXT, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from backend.db_connection import Base


class UserOrm(Base):
    __tablename__ = "user"

    id = Column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), 
        default=datetime.datetime.now(),
        server_default=text("CURRENT_TIMESTAMP")
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


class ChatSessionOrm(Base):
    __tablename__ = "chat_session"

    id = Column(
            UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        )
    user_id = Column(
        UUID,
        ForeignKey("user.id", ondelete="cascade", name="fk__session__user_id"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), default=datetime.datetime.now(datetime.UTC)
    )

class MessageOrm(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        UUID,
        ForeignKey("user.id", ondelete="cascade", name="fk__message__user_id"),
        nullable=False,
    )
    session_id = Column(
        UUID,
        ForeignKey("chat_session.id", ondelete="cascade", name="fk__message__session_id"),
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
