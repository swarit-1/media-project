"""Add CMS fields to assignments and PUBLISHED status

Revision ID: 002_cms_fields
Revises: 001_pitch
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_cms_fields'
down_revision: Union[str, None] = '001_pitch'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'published' to assignment_status enum
    op.execute("ALTER TYPE assignment_status ADD VALUE IF NOT EXISTS 'published' AFTER 'approved'")

    # Add CMS-specific columns to assignments
    op.add_column('assignments', sa.Column('draft_url', sa.String(500), nullable=True))
    op.add_column('assignments', sa.Column('final_url', sa.String(500), nullable=True))
    op.add_column('assignments', sa.Column('cms_post_id', sa.String(200), nullable=True))
    op.add_column('assignments', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('assignments', 'published_at')
    op.drop_column('assignments', 'cms_post_id')
    op.drop_column('assignments', 'final_url')
    op.drop_column('assignments', 'draft_url')
    # Note: PostgreSQL does not support removing values from enums
