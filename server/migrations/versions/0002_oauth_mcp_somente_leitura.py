"""oauth: clientes, códigos e refresh tokens do MCP somente leitura (ChatGPT)

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-06 09:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('oauth_clientes',
    sa.Column('client_id', sa.String(length=64), nullable=False),
    sa.Column('nome', sa.String(length=160), nullable=False),
    sa.Column('redirect_uris', sa.Text(), nullable=False),
    sa.Column('auth_metodo', sa.String(length=32), nullable=False),
    sa.Column('segredo_hash', sa.String(length=64), nullable=True),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ip', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('client_id')
    )
    op.create_table('oauth_codigos',
    sa.Column('codigo_hash', sa.String(length=64), nullable=False),
    sa.Column('client_id', sa.String(length=64), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('redirect_uri', sa.Text(), nullable=False),
    sa.Column('code_challenge', sa.String(length=128), nullable=False),
    sa.Column('escopo', sa.String(length=200), nullable=False),
    sa.Column('recurso', sa.String(length=300), nullable=False),
    sa.Column('expira_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['oauth_clientes.client_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('codigo_hash')
    )
    op.create_index(op.f('ix_oauth_codigos_client_id'), 'oauth_codigos', ['client_id'], unique=False)
    op.create_index(op.f('ix_oauth_codigos_usuario_id'), 'oauth_codigos', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_oauth_codigos_expira_em'), 'oauth_codigos', ['expira_em'], unique=False)
    op.create_table('oauth_refresh',
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('familia', sa.String(length=32), nullable=False),
    sa.Column('client_id', sa.String(length=64), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('escopo', sa.String(length=200), nullable=False),
    sa.Column('recurso', sa.String(length=300), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expira_em', sa.DateTime(timezone=True), nullable=False),
    sa.Column('usado', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['oauth_clientes.client_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('token_hash')
    )
    op.create_index(op.f('ix_oauth_refresh_familia'), 'oauth_refresh', ['familia'], unique=False)
    op.create_index(op.f('ix_oauth_refresh_client_id'), 'oauth_refresh', ['client_id'], unique=False)
    op.create_index(op.f('ix_oauth_refresh_usuario_id'), 'oauth_refresh', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_oauth_refresh_expira_em'), 'oauth_refresh', ['expira_em'], unique=False)


def downgrade() -> None:
    op.drop_table('oauth_refresh')
    op.drop_table('oauth_codigos')
    op.drop_table('oauth_clientes')
