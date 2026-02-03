"""Create payments, compliance_records, and vendor_ledger tables

Revision ID: 001_payment
Revises:
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = '001_payment'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create payment_status enum
    op.execute(
        "CREATE TYPE payment_status AS ENUM "
        "('pending', 'escrow_held', 'release_triggered', 'processing', 'completed', 'failed', 'refunded')"
    )

    # Create payment_type enum
    op.execute(
        "CREATE TYPE payment_type AS ENUM ('assignment', 'kill_fee', 'bonus', 'refund')"
    )

    # Create ledger_entry_type enum
    op.execute(
        "CREATE TYPE ledger_entry_type AS ENUM ('payment', 'kill_fee', 'bonus', 'refund', 'adjustment')"
    )

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('assignment_id', UUID(as_uuid=True), sa.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('newsroom_id', UUID(as_uuid=True), sa.ForeignKey('newsrooms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('freelancer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        # Payment details
        sa.Column('payment_type', sa.Enum('assignment', 'kill_fee', 'bonus', 'refund', name='payment_type', create_type=False), nullable=False),
        sa.Column('gross_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('platform_fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('net_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        # Stripe references
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('stripe_transfer_id', sa.String(255), nullable=True),
        sa.Column('stripe_charge_id', sa.String(255), nullable=True),
        # Status
        sa.Column('status', sa.Enum('pending', 'escrow_held', 'release_triggered', 'processing', 'completed', 'failed', 'refunded', name='payment_status', create_type=False), server_default='pending'),
        # Description
        sa.Column('description', sa.Text, nullable=True),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('escrow_held_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('release_triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_payments_assignment', 'payments', ['assignment_id'])
    op.create_index('idx_payments_newsroom', 'payments', ['newsroom_id'])
    op.create_index('idx_payments_freelancer', 'payments', ['freelancer_id'])
    op.create_index('idx_payments_status', 'payments', ['status'])

    # Create compliance_records table
    op.create_table(
        'compliance_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('freelancer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tax_year', sa.Integer, nullable=False),
        # Amounts
        sa.Column('total_gross_payments', sa.Numeric(12, 2), server_default='0.00'),
        sa.Column('total_platform_fees', sa.Numeric(12, 2), server_default='0.00'),
        sa.Column('total_net_payments', sa.Numeric(12, 2), server_default='0.00'),
        sa.Column('payment_count', sa.Integer, server_default='0'),
        # Tax info
        sa.Column('w9_received', sa.Boolean, server_default='false'),
        sa.Column('tin_last_four', sa.String(4), nullable=True),
        sa.Column('form_1099_generated', sa.Boolean, server_default='false'),
        sa.Column('form_1099_sent', sa.Boolean, server_default='false'),
        # Threshold
        sa.Column('threshold_1099', sa.Numeric(10, 2), server_default='600.00'),
        sa.Column('exceeds_threshold', sa.Boolean, server_default='false'),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('freelancer_id', 'tax_year', name='uq_compliance_freelancer_year'),
    )
    op.create_index('idx_compliance_freelancer', 'compliance_records', ['freelancer_id'])
    op.create_index('idx_compliance_year', 'compliance_records', ['tax_year'])

    # Create vendor_ledger table
    op.create_table(
        'vendor_ledger',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('payment_id', UUID(as_uuid=True), sa.ForeignKey('payments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('freelancer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('newsroom_id', UUID(as_uuid=True), sa.ForeignKey('newsrooms.id', ondelete='CASCADE'), nullable=False),
        # Entry details
        sa.Column('entry_type', sa.Enum('payment', 'kill_fee', 'bonus', 'refund', 'adjustment', name='ledger_entry_type', create_type=False), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('running_balance', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('description', sa.Text, nullable=True),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_vendor_ledger_freelancer', 'vendor_ledger', ['freelancer_id'])
    op.create_index('idx_vendor_ledger_newsroom', 'vendor_ledger', ['newsroom_id'])
    op.create_index('idx_vendor_ledger_created', 'vendor_ledger', ['created_at'])


def downgrade() -> None:
    op.drop_table('vendor_ledger')
    op.drop_table('compliance_records')
    op.drop_table('payments')
    op.execute('DROP TYPE ledger_entry_type')
    op.execute('DROP TYPE payment_type')
    op.execute('DROP TYPE payment_status')
