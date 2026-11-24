from uuid import UUID

from fastapi import APIRouter, Body, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate

from src.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from src.centro_treinamento.service import CentroTreinamentoService
from src.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    "/",
    summary="Criar um novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
    responses={
        status.HTTP_303_SEE_OTHER: {
            "description": "Já existe um centro de treinamento cadastrado com o nome informado."
        }
    },
)
async def post_centro_treinamento(
    db_session: DatabaseDependency,
    centro_treinamento_in: CentroTreinamentoIn = Body(...),
) -> CentroTreinamentoOut:
    centro = await CentroTreinamentoService.create(db_session, centro_treinamento_in)
    return CentroTreinamentoOut.model_validate(centro)


@router.get(
    "/",
    summary="Consultar todos os centros de treinamento (com paginação limit/offset)",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[CentroTreinamentoOut],
)
async def list_centros_treinamento(
    db_session: DatabaseDependency,
) -> LimitOffsetPage[CentroTreinamentoOut]:
    query = CentroTreinamentoService.get_all_query()
    return await paginate(db_session, query)


@router.get(
    "/{id}",
    summary="Consultar um centro de treinamento pelo ID (UUID)",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Centro de treinamento não encontrado."
        }
    },
)
async def get_centro_treinamento(
    id: UUID,
    db_session: DatabaseDependency,
) -> CentroTreinamentoOut:
    centro = await CentroTreinamentoService.get_by_id(db_session, id)
    return CentroTreinamentoOut.model_validate(centro)
