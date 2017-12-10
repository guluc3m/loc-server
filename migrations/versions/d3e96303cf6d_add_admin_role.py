"""Add admin role

Revision ID: d3e96303cf6d
Revises: 5dc8e201fa17
Create Date: 2017-12-10 18:49:26.177807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3e96303cf6d'
down_revision = '5dc8e201fa17'
branch_labels = None
depends_on = None


def upgrade():
    roles_table = sa.sql.table(
        'roles',
        sa.sql.column('name', sa.String)
    )

    op.bulk_insert(roles_table, [{'name': 'admin'}])


def downgrade():
    op.execute("DELETE FROM roles WHERE name=='admin'")
