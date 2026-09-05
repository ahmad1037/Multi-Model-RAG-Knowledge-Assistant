"""add full text search index

Revision ID: bdd4c96e7c7a
Revises: f231d7dfd63d
Create Date: 2026-09-05 14:22:50.529748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdd4c96e7c7a'
down_revision: Union[str, Sequence[str], None] = 'f231d7dfd63d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute(
        """
        ALTER TABLE document_chunks
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(
                to_tsvector(
                    'english',
                    coalesce(heading, '')
                ),
                'A'
            )
            ||
            setweight(
                to_tsvector(
                    'english',
                    coalesce(text, '')
                ),
                'B'
            )
        ) STORED
        """
    )

    op.execute(
        """
        CREATE INDEX
        ix_document_chunks_search_vector_gin
        ON document_chunks
        USING GIN (search_vector)
        """
    )

def downgrade() -> None:

    op.execute(
        """
        DROP INDEX IF EXISTS
        ix_document_chunks_search_vector_gin
        """
    )

    op.execute(
        """
        ALTER TABLE document_chunks
        DROP COLUMN IF EXISTS search_vector
        """
    )