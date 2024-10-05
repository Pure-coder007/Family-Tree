"""empty message

Revision ID: 29bd61d1d4af
Revises: 57459c0ae000
Create Date: 2024-10-05 15:15:48.703914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29bd61d1d4af'
down_revision = '57459c0ae000'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('otp', sa.String(length=6), nullable=True),
    sa.Column('token', sa.String(length=255), nullable=True),
    sa.Column('otp_expires_at', sa.DateTime(), nullable=True),
    sa.Column('token_expires_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_sessions_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_sessions'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_sessions')
    # ### end Alembic commands ###