"""empty message

Revision ID: cf9a3a5f71ad
Revises: 1d73fa51d486
Create Date: 2024-10-14 22:35:49.302130

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cf9a3a5f71ad'
down_revision = '1d73fa51d486'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gallery', schema=None) as batch_op:
        batch_op.alter_column('event_year',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=50),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gallery', schema=None) as batch_op:
        batch_op.alter_column('event_year',
               existing_type=sa.String(length=50),
               type_=mysql.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
