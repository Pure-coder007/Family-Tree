"""empty message

Revision ID: 9f7a5d3bb5c0
Revises: f96dce357d3c
Create Date: 2024-10-25 11:52:16.145208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f7a5d3bb5c0'
down_revision = 'f96dce357d3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('moderators', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('moderators', schema=None) as batch_op:
        batch_op.drop_column('role')

    # ### end Alembic commands ###
