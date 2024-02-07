"""add description field in glourbassets

Revision ID: 35cbee25a48b
Revises: ff0f4eb79c77
Create Date: 2024-02-07 15:55:27.603731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35cbee25a48b'
down_revision: Union[str, None] = 'ff0f4eb79c77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('glourbassets', sa.Column('description', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('glourbassets', 'description')
