"""empty message

Revision ID: 0112123dd53f
Revises: 6ddf0fb77428
Create Date: 2024-09-09 08:09:35.623821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0112123dd53f'
down_revision = '6ddf0fb77428'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('is_active',
               existing_type=sa.BOOLEAN(),
               type_=sa.String(length=80),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('is_active',
               existing_type=sa.String(length=80),
               type_=sa.BOOLEAN(),
               existing_nullable=False)

    # ### end Alembic commands ###
