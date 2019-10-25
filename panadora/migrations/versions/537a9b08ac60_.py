"""empty message

Revision ID: 537a9b08ac60
Revises: 
Create Date: 2019-10-22 18:39:09.543124

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '537a9b08ac60'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('token', sa.String(length=500), nullable=False),
    sa.Column('blacklisted_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('clusters',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('provider', sa.String(length=10), nullable=False),
    sa.Column('project_id', sa.String(length=20), nullable=True),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('zone', sa.String(length=20), nullable=False),
    sa.Column('master_node_type', sa.String(length=20), nullable=False),
    sa.Column('worker_node_type', sa.String(length=20), nullable=False),
    sa.Column('master_node_count', sa.Integer(), nullable=True),
    sa.Column('worker_node_count', sa.Integer(), nullable=True),
    sa.Column('network_range', sa.String(length=20), nullable=False),
    sa.Column('network_policy', sa.String(length=20), nullable=False),
    sa.Column('network_enabled', sa.Boolean(), nullable=True),
    sa.Column('kube_config', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('organization',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('policy', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('create_at', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provisioner',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('verbose_name', sa.String(length=256), nullable=False),
    sa.Column('engine', sa.String(length=256), nullable=False),
    sa.Column('state', sa.String(length=20), nullable=False),
    sa.Column('parameters', sqlalchemy_utils.types.json.JSONType(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('admin', sa.Boolean(), nullable=False),
    sa.Column('public_id', sa.String(length=100), nullable=True),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('password_hash', sa.String(length=100), nullable=True),
    sa.Column('registered_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('public_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('user_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_roles')
    op.drop_table('user')
    op.drop_table('roles')
    op.drop_table('provisioner')
    op.drop_table('organization')
    op.drop_table('clusters')
    op.drop_table('blacklist_tokens')
    # ### end Alembic commands ###
