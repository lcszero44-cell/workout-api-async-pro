from typing import Annotated

from pydantic import UUID4, Field, field_validator

from src.contrib.schemas import BaseSchema


class CategoriaIn(BaseSchema):
    """Schema de entrada/referência para uma categoria."""

    nome: Annotated[
        str,
        Field(
            description="Nome único da categoria de CrossFit",
            examples=["Scale", "RX", "Elite"],
            min_length=1,
            max_length=50,
        ),
    ]

    @field_validator("nome")
    @classmethod
    def strip_nome(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("O nome da categoria não pode ser vazio.")
        return cleaned


class CategoriaOut(CategoriaIn):
    """Schema completo de saída para uma categoria."""

    id: Annotated[UUID4, Field(description="Identificador UUID da categoria")]
    pk_id: Annotated[int, Field(description="Chave primária sequencial interna")]
