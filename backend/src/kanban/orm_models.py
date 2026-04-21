from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class BoardORM(Base):
    __tablename__ = "board"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    columns: Mapped[list["ColumnORM"]] = relationship(
        back_populates="board",
        cascade="all, delete-orphan",
        order_by="ColumnORM.position",
    )


class ColumnORM(Base):
    __tablename__ = "columns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    board_id: Mapped[int] = mapped_column(ForeignKey("board.id", ondelete="CASCADE"), nullable=False, index=True)

    board: Mapped["BoardORM"] = relationship(back_populates="columns")
    tasks: Mapped[list["TaskORM"]] = relationship(
        back_populates="column",
        cascade="all, delete-orphan",
        order_by="TaskORM.position",
    )


class TaskORM(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    assignee: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    column_id: Mapped[int] = mapped_column(ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True)

    column: Mapped["ColumnORM"] = relationship(back_populates="tasks")


class AccountORM(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    
    