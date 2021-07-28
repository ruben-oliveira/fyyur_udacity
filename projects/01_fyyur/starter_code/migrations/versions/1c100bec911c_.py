"""empty message

Revision ID: 1c100bec911c
Revises: a58d9ee27895
Create Date: 2021-07-19 09:29:47.711456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c100bec911c'
down_revision = 'a58d9ee27895'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('date', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###
