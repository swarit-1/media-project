"""Create squad_templates, squad_instances, and squad_members tables

Revision ID: 001_squad
Revises:
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

# revision identifiers, used by Alembic.
revision: str = '001_squad'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create squad_instance_status enum
    op.execute(
        "CREATE TYPE squad_instance_status AS ENUM ('forming', 'active', 'completed', 'disbanded')"
    )

    # Create squad_member_status enum
    op.execute(
        "CREATE TYPE squad_member_status AS ENUM ('invited', 'accepted', 'declined', 'removed')"
    )

    # Create squad_templates table
    op.create_table(
        'squad_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('newsroom_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('required_beats', ARRAY(sa.Text), nullable=False),
        sa.Column('required_roles', ARRAY(sa.Text), nullable=False),
        sa.Column('min_members', sa.Integer, server_default='2'),
        sa.Column('max_members', sa.Integer, server_default='10'),
        sa.Column('min_trust_score', sa.Float, nullable=True),
        sa.Column('preferred_tiers', ARRAY(sa.Text), nullable=True),
        sa.Column('metadata_json', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_squad_templates_newsroom', 'squad_templates', ['newsroom_id'])

    # Create squad_instances table
    op.create_table(
        'squad_instances',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('template_id', UUID(as_uuid=True), sa.ForeignKey('squad_templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('newsroom_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('project_brief', sa.Text, nullable=True),
        sa.Column('status', sa.Enum('forming', 'active', 'completed', 'disbanded', name='squad_instance_status', create_type=False), server_default='forming'),
        sa.Column('metadata_json', JSONB, nullable=True),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_squad_instances_template', 'squad_instances', ['template_id'])
    op.create_index('idx_squad_instances_newsroom', 'squad_instances', ['newsroom_id'])
    op.create_index('idx_squad_instances_status', 'squad_instances', ['status'])

    # Create squad_members table
    op.create_table(
        'squad_members',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('squad_id', UUID(as_uuid=True), sa.ForeignKey('squad_instances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('freelancer_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(100), nullable=False),
        sa.Column('beats', ARRAY(sa.Text), nullable=True),
        sa.Column('status', sa.Enum('invited', 'accepted', 'declined', 'removed', name='squad_member_status', create_type=False), server_default='invited'),
        sa.Column('invited_by', UUID(as_uuid=True), nullable=False),
        sa.Column('invitation_message', sa.Text, nullable=True),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_squad_members_squad', 'squad_members', ['squad_id'])
    op.create_index('idx_squad_members_freelancer', 'squad_members', ['freelancer_id'])
    op.create_index('idx_squad_members_status', 'squad_members', ['status'])


def downgrade() -> None:
    op.drop_table('squad_members')
    op.drop_table('squad_instances')
    op.drop_table('squad_templates')
    op.execute('DROP TYPE squad_member_status')
    op.execute('DROP TYPE squad_instance_status')
