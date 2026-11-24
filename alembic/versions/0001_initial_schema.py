"""Initial schema: categorias, centros_treinamento and atletas

Revision ID: 0001_initial_schema
Revises:
Create Date: 2025-05-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("pk_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("pk_id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_index("ix_categorias_id", "categorias", ["id"], unique=True)
    op.create_index("ix_categorias_nome", "categorias", ["nome"], unique=True)

    op.create_table(
        "centros_treinamento",
        sa.Column("pk_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=50), nullable=False),
        sa.Column("endereco", sa.String(length=100), nullable=False),
        sa.Column("proprietario", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("pk_id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_index("ix_centros_treinamento_id", "centros_treinamento", ["id"], unique=True)
    op.create_index("ix_centros_treinamento_nome", "centros_treinamento", ["nome"], unique=True)

    op.create_table(
        "atletas",
        sa.Column("pk_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column("cpf", sa.String(length=11), nullable=False),
        sa.Column("idade", sa.Integer(), nullable=False),
        sa.Column("peso", sa.Float(), nullable=False),
        sa.Column("altura", sa.Float(), nullable=False),
        sa.Column("sexo", sa.String(length=1), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("centro_treinamento_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.pk_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["centro_treinamento_id"],
            ["centros_treinamento.pk_id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("pk_id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("cpf"),
    )
    op.create_index("ix_atletas_id", "atletas", ["id"], unique=True)
    op.create_index("ix_atletas_nome", "atletas", ["nome"], unique=False)
    op.create_index("ix_atletas_cpf", "atletas", ["cpf"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_atletas_cpf", table_name="atletas")
    op.drop_index("ix_atletas_nome", table_name="atletas")
    op.drop_index("ix_atletas_id", table_name="atletas")
    op.drop_table("atletas")

    op.drop_index("ix_centros_treinamento_nome", table_name="centros_treinamento")
    op.drop_index("ix_centros_treinamento_id", table_name="centros_treinamento")
    op.drop_table("centros_treinamento")

    op.drop_index("ix_categorias_nome", table_name="categorias")
    op.drop_index("ix_categorias_id", table_name="categorias")
    op.drop_table("categorias")
