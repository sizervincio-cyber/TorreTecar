"""precos comerciais: campanha Fenatran (campanhas, lotes versionados, precos em centavos e auditoria)

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-09 10:30:00

Reversível: o downgrade remove só estas quatro tabelas; usuários, sessões, leads e OAuth não são tocados.
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('comercial_campanhas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chave', sa.String(length=40), nullable=False),
    sa.Column('nome', sa.String(length=160), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('versao', sa.Integer(), nullable=False),
    sa.Column('lote_atual_id', sa.Integer(), nullable=True),
    sa.Column('expira_em', sa.DateTime(timezone=True), nullable=True),
    sa.Column('metadados', sa.Text(), nullable=False),
    sa.Column('responsavel', sa.String(length=120), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("status IN ('draft','active','inactive','archived')", name='ck_comercial_campanhas_status'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comercial_campanhas_chave', 'comercial_campanhas', ['chave'], unique=True)
    op.create_table('comercial_lotes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('campanha_id', sa.Integer(), nullable=False),
    sa.Column('versao', sa.Integer(), nullable=False),
    sa.Column('arquivo_csv', sa.String(length=200), nullable=False),
    sa.Column('sha256_csv', sa.String(length=64), nullable=False),
    sa.Column('linhas', sa.Integer(), nullable=False),
    sa.Column('por_familia', sa.Text(), nullable=False),
    sa.Column('documentos', sa.Text(), nullable=False),
    sa.Column('conferencia', sa.Text(), nullable=False),
    sa.Column('diff', sa.Text(), nullable=False),
    sa.Column('manifesto', sa.Text(), nullable=False),
    sa.Column('executado_por', sa.String(length=120), nullable=False),
    sa.Column('executado_em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['campanha_id'], ['comercial_campanhas.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('campanha_id', 'versao', name='uq_comercial_lotes_campanha_versao')
    )
    op.create_index('ix_comercial_lotes_campanha_id', 'comercial_lotes', ['campanha_id'], unique=False)
    op.create_table('comercial_precos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('campanha_id', sa.Integer(), nullable=False),
    sa.Column('lote_id', sa.Integer(), nullable=False),
    sa.Column('familia', sa.String(length=12), nullable=False),
    sa.Column('modelo', sa.String(length=40), nullable=False),
    sa.Column('modelo_busca', sa.String(length=40), nullable=False),
    sa.Column('ano_modelo', sa.String(length=5), nullable=False),
    sa.Column('up', sa.String(length=4), nullable=False),
    sa.Column('variante', sa.String(length=20), nullable=False),
    sa.Column('configuracao', sa.String(length=5), nullable=False),
    sa.Column('preco_fabrica_5_10_centavos', sa.BigInteger(), nullable=False),
    sa.Column('preco_fabrica_11_15_centavos', sa.BigInteger(), nullable=False),
    sa.Column('preco_estoque_5_10_centavos', sa.BigInteger(), nullable=False),
    sa.Column('preco_estoque_11_15_centavos', sa.BigInteger(), nullable=False),
    sa.Column('source_file', sa.String(length=80), nullable=False),
    sa.Column('source_page', sa.Integer(), nullable=False),
    sa.CheckConstraint('preco_fabrica_5_10_centavos > 0 AND preco_fabrica_11_15_centavos > 0 AND '
                       'preco_estoque_5_10_centavos > 0 AND preco_estoque_11_15_centavos > 0',
                       name='ck_comercial_precos_positivos'),
    sa.ForeignKeyConstraint(['campanha_id'], ['comercial_campanhas.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['lote_id'], ['comercial_lotes.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lote_id', 'variante', name='uq_comercial_precos_lote_variante')
    )
    op.create_index('ix_comercial_precos_campanha_variante', 'comercial_precos', ['campanha_id', 'variante'], unique=False)
    op.create_index('ix_comercial_precos_lote_busca', 'comercial_precos', ['lote_id', 'modelo_busca'], unique=False)
    op.create_table('comercial_eventos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('campanha_id', sa.Integer(), nullable=False),
    sa.Column('acao', sa.String(length=30), nullable=False),
    sa.Column('de_status', sa.String(length=12), nullable=False),
    sa.Column('para_status', sa.String(length=12), nullable=False),
    sa.Column('usuario', sa.String(length=120), nullable=False),
    sa.Column('detalhe', sa.Text(), nullable=False),
    sa.Column('em', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['campanha_id'], ['comercial_campanhas.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comercial_eventos_campanha_id', 'comercial_eventos', ['campanha_id'], unique=False)
    op.create_index('ix_comercial_eventos_em', 'comercial_eventos', ['em'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_comercial_eventos_em', table_name='comercial_eventos')
    op.drop_index('ix_comercial_eventos_campanha_id', table_name='comercial_eventos')
    op.drop_table('comercial_eventos')
    op.drop_index('ix_comercial_precos_lote_busca', table_name='comercial_precos')
    op.drop_index('ix_comercial_precos_campanha_variante', table_name='comercial_precos')
    op.drop_table('comercial_precos')
    op.drop_index('ix_comercial_lotes_campanha_id', table_name='comercial_lotes')
    op.drop_table('comercial_lotes')
    op.drop_index('ix_comercial_campanhas_chave', table_name='comercial_campanhas')
    op.drop_table('comercial_campanhas')
