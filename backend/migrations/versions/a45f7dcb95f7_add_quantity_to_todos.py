"""add quantity to todos

Revision ID: a45f7dcb95f7
Revises: e1480fc92083
Create Date: 2025-06-24 21:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a45f7dcb95f7'
down_revision: Union[str, None] = 'e1480fc92083'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add quantity column."""
    op.add_column('todos', sa.Column('quantity', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove quantity column."""
    op.drop_column('todos', 'quantity')
