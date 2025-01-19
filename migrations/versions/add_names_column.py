"""Add names column

Revision ID: add_names_column
Revises: 
Create Date: 2024-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_names_column'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # SQLite doesn't support ALTER TABLE ADD COLUMN with JSON type
    # So we need to use TEXT type instead
    with op.batch_alter_table('note') as batch_op:
        batch_op.add_column(sa.Column('names', sa.Text, nullable=True))

def downgrade():
    with op.batch_alter_table('note') as batch_op:
        batch_op.drop_column('names') 