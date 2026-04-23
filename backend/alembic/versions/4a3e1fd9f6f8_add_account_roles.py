"""add account roles

Revision ID: 4a3e1fd9f6f8
Revises: b4e1a4d7c2ab
Create Date: 2026-04-23 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a3e1fd9f6f8"
down_revision: Union[str, Sequence[str], None] = "b4e1a4d7c2ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "accounts",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="read"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("accounts", "role")