"""Initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-01-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create note table with all columns
    op.create_table('note',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('mood_score', sa.Float(), nullable=True),
        sa.Column('journal_date', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('names', sa.Text(), nullable=True),
        sa.Column('weekly_summary', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('note') 