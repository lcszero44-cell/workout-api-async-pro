from typing import Annotated

from pydantic import UUID4, Field, field_validator

from src.contrib.schemas import BaseSchema


class CentroTreinamentoAtleta(BaseSchema):
    """Schema enxuto de referência ao Centro de Treinamento nos payloads de Atleta."""

    nome: Annotated[
        str,
        Field(
            description="Nome do centro de treinamento",
            examples=["CT Iron Box"],
            min_length=1,
            max_length=50,
        ),
    ]

    @field_validator("nome")
    @classmethod
    def strip_nome(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("O nome do centro de treinamento não pode ser vazio.")
        return cleaned


class CentroTreinamentoIn(CentroTreinamentoAtleta):
    """Schema de entrada completo para criação de um Centro de Treinamento."""

    endereco: Annotated[
        str,
        Field(
            description="Endereço do centro de treinamento",
            examples=["Av. Paulista, 1500 - São Paulo/SP"],
            min_length=1,
            max_length=100,
        ),
    ]
    proprietario: Annotated[
        str,
        Field(
            description="Nome do proprietário/head coach",
            examples=["Marcos Silva"],
            min_length=1,
            max_length=50,
        ),
    ]

    @field_validator("endereco", "proprietario")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("O campo não pode ser vazio.")
        return cleaned


class CentroTreinamentoOut(CentroTreinamentoIn):
    """Schema completo de saída para um Centro de Treinamento."""

    id: Annotated[UUID4, Field(description="Identificador UUID do centro de treinamento")]
    pk_id: Annotated[int, Field(description="Chave primária sequencial interna")]
