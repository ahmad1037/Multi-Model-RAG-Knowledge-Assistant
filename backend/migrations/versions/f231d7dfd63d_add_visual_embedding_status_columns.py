"""add visual embedding status index

Revision ID: f231d7dfd63d
Revises: 28ec12dbae31
Create Date: 2026-09-05 11:18:06.373304
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f231d7dfd63d"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "28ec12dbae31"
branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None
depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    """Create the visual embedding status index."""

    op.create_index(
        "ix_visual_assets_clip_embedding_status",
        "visual_assets",
        ["clip_embedding_status"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the visual embedding status index."""

    op.drop_index(
        "ix_visual_assets_clip_embedding_status",
        table_name="visual_assets",
    )