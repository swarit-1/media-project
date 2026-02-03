"""Initial schema for users, profiles, and newsrooms

Revision ID: 001_initial
Revises:
Create Date: 2026-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_role enum
    op.execute("CREATE TYPE user_role AS ENUM ('freelancer', 'editor', 'admin')")

    # Create user_status enum
    op.execute("CREATE TYPE user_status AS ENUM ('pending', 'active', 'suspended', 'deactivated')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('auth_provider', sa.String(50), server_default='local'),
        sa.Column('auth_provider_id', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('freelancer', 'editor', 'admin', name='user_role', create_type=False), nullable=False),
        sa.Column('status', sa.Enum('pending', 'active', 'suspended', 'deactivated', name='user_status', create_type=False), server_default='pending'),
        sa.Column('email_verified', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role_status', 'users', ['role', 'status'])

    # Create freelancer_profiles table
    op.create_table(
        'freelancer_profiles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('bio', sa.Text, nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        # Location
        sa.Column('home_zip', sa.String(10), nullable=True),
        sa.Column('home_city', sa.String(100), nullable=True),
        sa.Column('home_state', sa.String(50), nullable=True),
        sa.Column('home_country', sa.String(50), server_default='US'),
        sa.Column('willing_to_travel_miles', sa.Integer, server_default='50'),
        # Beats & expertise
        sa.Column('primary_beats', ARRAY(sa.Text), nullable=True),
        sa.Column('secondary_beats', ARRAY(sa.Text), nullable=True),
        sa.Column('languages', ARRAY(sa.Text), server_default=sa.text("ARRAY['en']::text[]")),
        # Availability
        sa.Column('availability_status', sa.String(20), server_default='available'),
        sa.Column('weekly_capacity_hours', sa.Integer, server_default='40'),
        # Rates
        sa.Column('hourly_rate_min', sa.Numeric(10, 2), nullable=True),
        sa.Column('hourly_rate_max', sa.Numeric(10, 2), nullable=True),
        sa.Column('per_word_rate', sa.Numeric(6, 4), nullable=True),
        sa.Column('day_rate', sa.Numeric(10, 2), nullable=True),
        # Verification
        sa.Column('identity_verified', sa.Boolean, server_default='false'),
        sa.Column('portfolio_verified', sa.Boolean, server_default='false'),
        sa.Column('tax_info_complete', sa.Boolean, server_default='false'),
        sa.Column('bank_info_complete', sa.Boolean, server_default='false'),
        # Scores
        sa.Column('trust_score', sa.Numeric(3, 2), server_default='0.50'),
        sa.Column('quality_score', sa.Numeric(3, 2), server_default='0.50'),
        sa.Column('reliability_score', sa.Numeric(3, 2), server_default='0.50'),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_freelancer_profiles_beats', 'freelancer_profiles', ['primary_beats'], postgresql_using='gin')
    op.create_index('idx_freelancer_profiles_scores', 'freelancer_profiles', ['trust_score', 'quality_score'])

    # Create editor_profiles table
    op.create_table(
        'editor_profiles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('bio', sa.Text, nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # Create newsrooms table
    op.create_table(
        'newsrooms',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        # Configuration
        sa.Column('cms_type', sa.String(50), nullable=True),
        sa.Column('cms_webhook_url', sa.String(500), nullable=True),
        sa.Column('payment_terms_days', sa.Integer, server_default='30'),
        # Compliance
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('billing_address', JSONB, nullable=True),
        # Style
        sa.Column('style_guide_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # Create newsroom_memberships table
    op.create_table(
        'newsroom_memberships',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('newsroom_id', UUID(as_uuid=True), sa.ForeignKey('newsrooms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permissions', ARRAY(sa.Text), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('newsroom_id', 'user_id', name='uq_newsroom_memberships_newsroom_user'),
    )


def downgrade() -> None:
    op.drop_table('newsroom_memberships')
    op.drop_table('newsrooms')
    op.drop_table('editor_profiles')
    op.drop_table('freelancer_profiles')
    op.drop_table('users')
    op.execute('DROP TYPE user_status')
    op.execute('DROP TYPE user_role')
