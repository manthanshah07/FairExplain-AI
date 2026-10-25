"""Add family_id, replaced_by, and rotated_at to refresh_tokens.

Revision ID: c2b3d4e5f6a7
Revises: b1a2c3d4e5f6
Create Date: 2026-10-25 20:10:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c2b3d4e5f6a7'
down_revision = 'b1a2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add family_id with UUID generator default for existing rows
    op.add_column(
        'refresh_tokens',
        sa.Column(
            'family_id',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
    )
    op.create_index(op.f('ix_refresh_tokens_family_id'), 'refresh_tokens', ['family_id'], unique=False)

    # 2. Add replaced_by tracking immediate descendant JTI
    op.add_column(
        'refresh_tokens',
        sa.Column('replaced_by', sa.String(length=64), nullable=True),
    )
    op.create_index(op.f('ix_refresh_tokens_replaced_by'), 'refresh_tokens', ['replaced_by'], unique=False)

    # 3. Add rotated_at timestamp
    op.add_column(
        'refresh_tokens',
        sa.Column('rotated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('refresh_tokens', 'rotated_at')
    op.drop_index(op.f('ix_refresh_tokens_replaced_by'), table_name='refresh_tokens')
    op.drop_column('refresh_tokens', 'replaced_by')
    op.drop_index(op.f('ix_refresh_tokens_family_id'), table_name='refresh_tokens')
    op.drop_column('refresh_tokens', 'family_id')
