from uuid import UUID

from fastapi import APIRouter, Body, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate

from src.categorias.schemas import CategoriaIn, CategoriaOut
from src.categorias.service import CategoriaService
from src.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    "/",
    summary="Criar uma nova categoria",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
    responses={
        status.HTTP_303_SEE_OTHER: {
            "description": "Já existe uma categoria cadastrada com o nome informado."
        }
    },
)
async def post_categoria(
    db_session: DatabaseDependency,
    categoria_in: CategoriaIn = Body(...),
) -> CategoriaOut:
    categoria = await CategoriaService.create(db_session, categoria_in)
    return CategoriaOut.model_validate(categoria)


@router.get(
    "/",
    summary="Consultar todas as categorias (com paginação limit/offset)",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[CategoriaOut],
)
async def list_categorias(
    db_session: DatabaseDependency,
) -> LimitOffsetPage[CategoriaOut]:
    query = CategoriaService.get_all_query()
    return await paginate(db_session, query)


@router.get(
    "/{id}",
    summary="Consultar uma categoria pelo ID (UUID)",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Categoria não encontrada."}
    },
)
async def get_categoria(
    id: UUID,
    db_session: DatabaseDependency,
) -> CategoriaOut:
    categoria = await CategoriaService.get_by_id(db_session, id)
    return CategoriaOut.model_validate(categoria)
