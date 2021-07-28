"""empty message

Revision ID: 1bf13bfa2c8b
Revises: 7113f1059e0e
Create Date: 2021-07-15 14:50:33.457213

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bf13bfa2c8b'
down_revision = '7113f1059e0e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows_table', sa.Column('date', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows_table', 'date')
    # ### end Alembic commands ###