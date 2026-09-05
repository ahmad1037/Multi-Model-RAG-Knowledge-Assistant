"""configure clip visual embeddings

Revision ID: 28ec12dbae31
Revises: c88d90ccf975
Create Date: 2026-09-04 20:48:24.055595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28ec12dbae31'
down_revision: Union[str, Sequence[str], None] = 'c88d90ccf975'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "visual_assets",
        sa.Column(
            "clip_pretrained",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "visual_assets",
        sa.Column(
            "clip_embedding_status",
            sa.String(length=50),
            server_default="pending",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("visual_assets", "clip_embedding_status")
    op.drop_column("visual_assets", "clip_pretrained")