"""Add journal_date column

Revision ID: xxx
Revises: xxx
Create Date: 2024-01-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('note', sa.Column('journal_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')))

def downgrade():
    op.drop_column('note', 'journal_date') 