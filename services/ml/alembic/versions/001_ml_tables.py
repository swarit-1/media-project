"""Create portfolio_items, style_fingerprints, and topic_classifications tables

Revision ID: 001_ml
Revises:
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

# revision identifiers, used by Alembic.
revision: str = '001_ml'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create outlet_tier enum
    op.execute(
        "CREATE TYPE outlet_tier AS ENUM ('tier1', 'tier2', 'tier3', 'unknown')"
    )

    # Create verification_status enum
    op.execute(
        "CREATE TYPE verification_status AS ENUM ('pending', 'verified', 'rejected', 'disputed')"
    )

    # Create portfolio_items table
    op.create_table(
        'portfolio_items',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('freelancer_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        # Article metadata
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('publication', sa.String(255), nullable=True),
        sa.Column('published_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('byline', sa.String(500), nullable=True),
        # Content analysis
        sa.Column('word_count', sa.Integer, nullable=True),
        sa.Column('excerpt', sa.Text, nullable=True),
        sa.Column('topics', ARRAY(sa.Text), nullable=True),
        sa.Column('tone_profile', JSONB, nullable=True),
        # Classification
        sa.Column('outlet_tier', sa.Enum('tier1', 'tier2', 'tier3', 'unknown', name='outlet_tier', create_type=False), server_default='unknown'),
        sa.Column('geo_focus', ARRAY(sa.Text), nullable=True),
        # Verification
        sa.Column('verification_status', sa.Enum('pending', 'verified', 'rejected', 'disputed', name='verification_status', create_type=False), server_default='pending'),
        sa.Column('verification_method', sa.String(50), nullable=True),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('scraped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_portfolio_items_freelancer', 'portfolio_items', ['freelancer_id'])
    op.create_index('idx_portfolio_items_topics', 'portfolio_items', ['topics'], postgresql_using='gin')
    op.create_index('idx_portfolio_items_verification', 'portfolio_items', ['verification_status'])

    # Create style_fingerprints table
    op.create_table(
        'style_fingerprints',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(20), nullable=False),
        # Style metrics
        sa.Column('avg_sentence_length', sa.Numeric(5, 2), nullable=True),
        sa.Column('passive_voice_ratio', sa.Numeric(5, 4), nullable=True),
        sa.Column('narrative_score', sa.Numeric(5, 4), nullable=True),
        sa.Column('analytical_score', sa.Numeric(5, 4), nullable=True),
        sa.Column('explanatory_score', sa.Numeric(5, 4), nullable=True),
        sa.Column('citation_density', sa.Numeric(5, 4), nullable=True),
        sa.Column('headline_style', sa.String(20), nullable=True),
        sa.Column('similar_to_outlets', ARRAY(sa.String(100)), nullable=True),
        # Embedding vector (384 dimensions)
        sa.Column('style_embedding', sa.Column('vector(384)'), nullable=True),
        # Statistics
        sa.Column('sample_size', sa.Integer, server_default='0'),
        # Metadata
        sa.Column('metadata_json', JSONB, nullable=True),
        # Timestamps
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('entity_id', 'entity_type', name='uq_style_fingerprint_entity'),
    )
    op.create_index('idx_style_fingerprints_entity', 'style_fingerprints', ['entity_id', 'entity_type'])

    # Create IVFFlat index for approximate nearest neighbor search on embeddings
    op.execute(
        "CREATE INDEX idx_style_embedding_ivf ON style_fingerprints "
        "USING ivfflat (style_embedding vector_cosine_ops) WITH (lists = 100)"
    )

    # Create topic_classifications table
    op.create_table(
        'topic_classifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(20), nullable=False),
        # Classification results
        sa.Column('primary_topic', sa.String(100), nullable=False),
        sa.Column('primary_confidence', sa.Numeric(5, 4), nullable=False),
        sa.Column('secondary_topic', sa.String(100), nullable=True),
        sa.Column('secondary_confidence', sa.Numeric(5, 4), nullable=True),
        sa.Column('all_scores', JSONB, nullable=True),
        # Timestamps
        sa.Column('classified_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_topic_classifications_entity', 'topic_classifications', ['entity_id', 'entity_type'])
    op.create_index('idx_topic_classifications_primary', 'topic_classifications', ['primary_topic'])


def downgrade() -> None:
    op.drop_table('topic_classifications')
    op.execute('DROP INDEX IF EXISTS idx_style_embedding_ivf')
    op.drop_table('style_fingerprints')
    op.drop_table('portfolio_items')
    op.execute('DROP TYPE verification_status')
    op.execute('DROP TYPE outlet_tier')
