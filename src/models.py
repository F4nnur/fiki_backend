from src.db import Base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    func,
    ForeignKey,
    select,
    column,
    text,
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    fio = Column(String)
    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        default=select(column("id"))
        .where(column("name") == "user")
        .select_from(text("roles")),
    )
    role = relationship("Role", back_populates="users", lazy="joined")
    summaries = relationship(
        "Summary",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
        order_by="Summary.id",
    )
    comments = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
        order_by="Comment.id",
    )


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    users = relationship("User", back_populates="role", uselist=True)


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="summaries", lazy="joined")
    comments = relationship(
        "Comment",
        back_populates="summary",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin",
        order_by="Comment.id",
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    text = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    summary_id = Column(Integer, ForeignKey("summaries.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="comments", lazy="joined")
    summary = relationship("Summary", back_populates="comments", lazy="joined")
