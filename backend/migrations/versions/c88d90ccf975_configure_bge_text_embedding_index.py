"""configure bge text embedding index

Revision ID: c88d90ccf975
Revises: 46c845503c04
Create Date: 2026-09-04 10:44:17.653398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c88d90ccf975'
down_revision: Union[str, Sequence[str], None] = '46c845503c04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute(
        """
        ALTER TABLE document_chunks
        ALTER COLUMN embedding
        TYPE vector(384)
        USING embedding::vector(384)
        """
    )

    op.execute(
        """
        CREATE INDEX
        ix_document_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw
        (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:

    op.execute(
        """
        DROP INDEX IF EXISTS
        ix_document_chunks_embedding_hnsw
        """
    )

    op.execute(
        """
        ALTER TABLE document_chunks
        ALTER COLUMN embedding
        TYPE vector
        USING embedding::vector
        """
    )