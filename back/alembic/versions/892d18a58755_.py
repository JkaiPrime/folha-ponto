"""empty message

Revision ID: 892d18a58755
Revises: 5b46b80ea31e
Create Date: 2025-07-25 09:49:51.255428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '892d18a58755'
down_revision: Union[str, None] = '5b46b80ea31e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
