from uuid import UUID

from fastapi import APIRouter, Body, Query, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate

from src.atleta.schemas import AtletaIn, AtletaOut, AtletaOutResumo, AtletaUpdate
from src.atleta.service import AtletaService
from src.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    "/",
    summary="Criar um novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
    responses={
        status.HTTP_303_SEE_OTHER: {
            "description": "Já existe um atleta cadastrado com o cpf informado."
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Categoria ou Centro de Treinamento não encontrado."
        },
    },
)
async def post_atleta(
    db_session: DatabaseDependency,
    atleta_in: AtletaIn = Body(...),
) -> AtletaOut:
    atleta = await AtletaService.create(db_session, atleta_in)
    return AtletaOut.model_validate(atleta)


@router.get(
    "/",
    summary="Consultar atletas com filtros (nome, cpf), paginação e response customizado",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[AtletaOutResumo],
)
async def list_atletas(
    db_session: DatabaseDependency,
    nome: str | None = Query(
        default=None,
        description="Filtrar atletas pelo nome (busca parcial/exata case-insensitive)",
        examples=["Lucas"],
    ),
    cpf: str | None = Query(
        default=None,
        description="Filtrar atletas pelo CPF (busca exata sanitizada — aceita máscara ou dígitos)",
        examples=["11122233344"],
    ),
) -> LimitOffsetPage[AtletaOutResumo]:
    query = AtletaService.get_all_query(nome=nome, cpf=cpf)
    return await paginate(db_session, query)


@router.get(
    "/{id}",
    summary="Consultar detalhes completos de um atleta pelo ID (UUID)",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Atleta não encontrado."}
    },
)
async def get_atleta(
    id: UUID,
    db_session: DatabaseDependency,
) -> AtletaOut:
    atleta = await AtletaService.get_by_id(db_session, id)
    return AtletaOut.model_validate(atleta)


@router.patch(
    "/{id}",
    summary="Editar parcialmente um atleta pelo ID (UUID)",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
    responses={
        status.HTTP_303_SEE_OTHER: {
            "description": "Já existe um atleta cadastrado com o cpf informado."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Atleta não encontrado."},
    },
)
async def patch_atleta(
    id: UUID,
    db_session: DatabaseDependency,
    atleta_up: AtletaUpdate = Body(...),
) -> AtletaOut:
    atleta = await AtletaService.update(db_session, id, atleta_up)
    return AtletaOut.model_validate(atleta)


@router.delete(
    "/{id}",
    summary="Remover um atleta pelo ID (UUID)",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Atleta não encontrado."}
    },
)
async def delete_atleta(
    id: UUID,
    db_session: DatabaseDependency,
) -> None:
    await AtletaService.delete(db_session, id)
