"""Create pitch_windows, pitches, and assignments tables

Revision ID: 001_pitch
Revises:
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

# revision identifiers, used by Alembic.
revision: str = '001_pitch'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pitch_window_status enum
    op.execute(
        "CREATE TYPE pitch_window_status AS ENUM ('draft', 'open', 'closed', 'cancelled')"
    )

    # Create pitch_status enum
    op.execute(
        "CREATE TYPE pitch_status AS ENUM ('draft', 'submitted', 'under_review', 'accepted', 'rejected', 'withdrawn')"
    )

    # Create assignment_status enum
    op.execute(
        "CREATE TYPE assignment_status AS ENUM ('assigned', 'in_progress', 'submitted', 'revision_requested', 'approved', 'killed')"
    )

    # Create pitch_windows table
    op.create_table(
        'pitch_windows',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('newsroom_id', UUID(as_uuid=True), sa.ForeignKey('newsrooms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('editor_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('beats', ARRAY(sa.Text), nullable=False),
        sa.Column('requirements', sa.Text, nullable=True),
        # Budget
        sa.Column('budget_min', sa.Numeric(10, 2), nullable=True),
        sa.Column('budget_max', sa.Numeric(10, 2), nullable=True),
        sa.Column('rate_type', sa.String(20), server_default='per_word'),
        # Constraints
        sa.Column('max_pitches', sa.Integer, server_default='50'),
        sa.Column('current_pitch_count', sa.Integer, server_default='0'),
        # Timing
        sa.Column('opens_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('closes_at', sa.DateTime(timezone=True), nullable=False),
        # Status
        sa.Column('status', sa.Enum('draft', 'open', 'closed', 'cancelled', name='pitch_window_status', create_type=False), server_default='draft'),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_pitch_windows_newsroom', 'pitch_windows', ['newsroom_id'])
    op.create_index('idx_pitch_windows_editor', 'pitch_windows', ['editor_id'])
    op.create_index('idx_pitch_windows_status', 'pitch_windows', ['status'])
    op.create_index('idx_pitch_windows_beats', 'pitch_windows', ['beats'], postgresql_using='gin')

    # Create pitches table
    op.create_table(
        'pitches',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('pitch_window_id', UUID(as_uuid=True), sa.ForeignKey('pitch_windows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('freelancer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        # Content
        sa.Column('headline', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('approach', sa.Text, nullable=True),
        sa.Column('estimated_word_count', sa.Integer, nullable=True),
        # Rates
        sa.Column('proposed_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('proposed_rate_type', sa.String(20), nullable=True),
        sa.Column('estimated_delivery_days', sa.Integer, nullable=True),
        # Status
        sa.Column('status', sa.Enum('draft', 'submitted', 'under_review', 'accepted', 'rejected', 'withdrawn', name='pitch_status', create_type=False), server_default='draft'),
        # Editor feedback
        sa.Column('editor_notes', sa.Text, nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_pitches_window', 'pitches', ['pitch_window_id'])
    op.create_index('idx_pitches_freelancer', 'pitches', ['freelancer_id'])
    op.create_index('idx_pitches_status', 'pitches', ['status'])

    # Create assignments table
    op.create_table(
        'assignments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('pitch_id', UUID(as_uuid=True), sa.ForeignKey('pitches.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('freelancer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('editor_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('newsroom_id', UUID(as_uuid=True), sa.ForeignKey('newsrooms.id', ondelete='CASCADE'), nullable=False),
        # Details
        sa.Column('agreed_rate', sa.Numeric(10, 2), nullable=False),
        sa.Column('rate_type', sa.String(20), nullable=False),
        sa.Column('word_count_target', sa.Integer, nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=False),
        # Status
        sa.Column('status', sa.Enum('assigned', 'in_progress', 'submitted', 'revision_requested', 'approved', 'killed', name='assignment_status', create_type=False), server_default='assigned'),
        # Revision tracking
        sa.Column('revision_count', sa.Integer, server_default='0'),
        sa.Column('max_revisions', sa.Integer, server_default='2'),
        sa.Column('revision_notes', sa.Text, nullable=True),
        # Content delivery
        sa.Column('content_url', sa.String(500), nullable=True),
        sa.Column('final_word_count', sa.Integer, nullable=True),
        # Kill fee
        sa.Column('kill_fee_percentage', sa.Numeric(5, 2), server_default='25.00'),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_assignments_freelancer', 'assignments', ['freelancer_id'])
    op.create_index('idx_assignments_editor', 'assignments', ['editor_id'])
    op.create_index('idx_assignments_newsroom', 'assignments', ['newsroom_id'])
    op.create_index('idx_assignments_status', 'assignments', ['status'])


def downgrade() -> None:
    op.drop_table('assignments')
    op.drop_table('pitches')
    op.drop_table('pitch_windows')
    op.execute('DROP TYPE assignment_status')
    op.execute('DROP TYPE pitch_status')
    op.execute('DROP TYPE pitch_window_status')
