from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table

# https://docs.sqlalchemy.org/en/20/core/metadata.html#accessing-tables-and-columns

metadata_obj = MetaData()

board = Table(
    "board",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
)


columns = Table(
    "columns",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("position", Integer, nullable=False),
    Column("board_id", Integer, ForeignKey("board.id", ondelete="CASCADE"), nullable=False, index=True),
)

tasks = Table(
    "tasks",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("column_id", Integer, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("title", String(50), nullable=False),
    Column("description", String(200), nullable=False),
    Column("assignee", String(50), nullable=False, default=""),
    Column("position", Integer, nullable=False),
)