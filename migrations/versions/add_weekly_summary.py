"""Add weekly_summary column

Revision ID: add_weekly_summary
Revises: add_names_column
Create Date: 2024-01-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_weekly_summary'
down_revision = 'add_names_column'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('note') as batch_op:
        batch_op.add_column(sa.Column('weekly_summary', sa.Text, nullable=True))

def downgrade():
    with op.batch_alter_table('note') as batch_op:
        batch_op.drop_column('weekly_summary') 