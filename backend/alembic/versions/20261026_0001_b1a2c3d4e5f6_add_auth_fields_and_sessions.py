"""Add auth fields to users and create refresh_tokens table.

Revision ID: b1a2c3d4e5f6
Revises: a340bbc9e1be
Create Date: 2026-10-25 19:05:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b1a2c3d4e5f6'
down_revision = 'a340bbc9e1be'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add is_verified to users
    op.add_column(
        'users',
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    )

    # 2. Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('jti', sa.String(length=64), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('revoked', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_jti'), 'refresh_tokens', ['jti'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_revoked'), 'refresh_tokens', ['revoked'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_tokens_expires_at'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_revoked'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_jti'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_column('users', 'is_verified')
