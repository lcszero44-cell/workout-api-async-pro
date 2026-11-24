import re
from typing import Annotated

from pydantic import Field, PositiveFloat, field_validator

from src.categorias.schemas import CategoriaIn
from src.centro_treinamento.schemas import CentroTreinamentoAtleta
from src.contrib.schemas import BaseSchema, OutMixin


def sanitize_cpf(value: str) -> str:
    """Remove pontuação e espaços de um CPF, mantendo apenas dígitos numéricos."""
    return re.sub(r"\D", "", value)


class AtletaBase(BaseSchema):
    """Atributos nucleares de um Atleta de CrossFit."""

    nome: Annotated[
        str,
        Field(
            description="Nome completo do atleta",
            examples=["Lucas Mendes"],
            min_length=2,
            max_length=80,
        ),
    ]
    cpf: Annotated[
        str,
        Field(
            description="CPF do atleta (11 dígitos; aceita entrada com ou sem máscara)",
            examples=["12345678901"],
            min_length=11,
            max_length=14,
        ),
    ]
    idade: Annotated[
        int,
        Field(description="Idade do atleta em anos", examples=[28], ge=12, le=120),
    ]
    peso: Annotated[
        PositiveFloat,
        Field(description="Peso corporal em kg", examples=[78.5], le=350.0),
    ]
    altura: Annotated[
        PositiveFloat,
        Field(description="Altura em metros", examples=[1.78], le=2.60),
    ]
    sexo: Annotated[
        str,
        Field(
            description="Sexo do atleta ('M', 'F' ou 'O')",
            examples=["M"],
            min_length=1,
            max_length=1,
        ),
    ]
    categoria: Annotated[
        CategoriaIn,
        Field(description="Categoria de competição do atleta"),
    ]
    centro_treinamento: Annotated[
        CentroTreinamentoAtleta,
        Field(description="Centro de treinamento (Box) vinculado ao atleta"),
    ]

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("O nome do atleta deve ter ao menos 2 caracteres.")
        return cleaned

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        digits = sanitize_cpf(value)
        if len(digits) != 11:
            raise ValueError("O CPF deve conter exatamente 11 dígitos numéricos.")
        return digits

    @field_validator("sexo")
    @classmethod
    def validate_sexo(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"M", "F", "O"}:
            raise ValueError("O campo sexo deve ser 'M', 'F' ou 'O'.")
        return normalized


class AtletaIn(AtletaBase):
    """Schema de entrada para cadastro de um novo Atleta."""


class AtletaOut(AtletaBase, OutMixin):
    """Schema detalhado de saída para consultas unitárias (`GET /atletas/{id}`)."""

    pk_id: Annotated[int, Field(description="Chave primária sequencial interna")]


class AtletaOutResumo(BaseSchema):
    """Response customizado exclusivo para listagem geral (`GET /atletas/`).

    Retorna estritamente: nome, centro_treinamento e categoria (requisito DIO).
    """

    nome: Annotated[str, Field(description="Nome do atleta", examples=["Lucas Mendes"])]
    centro_treinamento: Annotated[
        CentroTreinamentoAtleta,
        Field(description="Centro de treinamento do atleta"),
    ]
    categoria: Annotated[
        CategoriaIn,
        Field(description="Categoria de competição do atleta"),
    ]


class AtletaUpdate(BaseSchema):
    """Schema de atualização parcial (`PATCH /atletas/{id}`)."""

    nome: Annotated[
        str | None,
        Field(default=None, description="Novo nome do atleta", min_length=2, max_length=80),
    ]
    cpf: Annotated[
        str | None,
        Field(default=None, description="Novo CPF do atleta", min_length=11, max_length=14),
    ]
    idade: Annotated[
        int | None,
        Field(default=None, description="Nova idade do atleta", ge=12, le=120),
    ]
    peso: Annotated[
        PositiveFloat | None,
        Field(default=None, description="Novo peso do atleta em kg", le=350.0),
    ]
    altura: Annotated[
        PositiveFloat | None,
        Field(default=None, description="Nova altura do atleta em metros", le=2.60),
    ]
    sexo: Annotated[
        str | None,
        Field(default=None, description="Novo sexo ('M', 'F' ou 'O')", min_length=1, max_length=1),
    ]
    categoria: Annotated[
        CategoriaIn | None,
        Field(default=None, description="Nova categoria do atleta"),
    ]
    centro_treinamento: Annotated[
        CentroTreinamentoAtleta | None,
        Field(default=None, description="Novo centro de treinamento do atleta"),
    ]

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("O nome do atleta deve ter ao menos 2 caracteres.")
        return cleaned

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str | None) -> str | None:
        if value is None:
            return None
        digits = sanitize_cpf(value)
        if len(digits) != 11:
            raise ValueError("O CPF deve conter exatamente 11 dígitos numéricos.")
        return digits

    @field_validator("sexo")
    @classmethod
    def validate_sexo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in {"M", "F", "O"}:
            raise ValueError("O campo sexo deve ser 'M', 'F' ou 'O'.")
        return normalized
