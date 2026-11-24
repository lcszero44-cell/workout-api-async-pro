from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.categorias.models import CategoriaModel
from src.categorias.schemas import CategoriaIn
from src.contrib.exceptions import DuplicateResourceError, ResourceNotFoundError


class CategoriaService:
    """Camada de serviço assíncrona para operações de domínio de Categorias."""

    @staticmethod
    async def create(db_session: AsyncSession, categoria_in: CategoriaIn) -> CategoriaModel:
        categoria = CategoriaModel(nome=categoria_in.nome)
        db_session.add(categoria)
        try:
            await db_session.commit()
            await db_session.refresh(categoria)
            return categoria
        except IntegrityError as exc:
            await db_session.rollback()
            raise DuplicateResourceError(
                detail=f"Já existe uma categoria cadastrada com o nome: {categoria_in.nome}"
            ) from exc

    @staticmethod
    def get_all_query() -> Select[tuple[CategoriaModel]]:
        return select(CategoriaModel).order_by(CategoriaModel.pk_id.asc())

    @staticmethod
    async def get_by_id(db_session: AsyncSession, categoria_id: UUID) -> CategoriaModel:
        stmt = select(CategoriaModel).where(CategoriaModel.id == categoria_id)
        categoria = (await db_session.execute(stmt)).scalars().first()
        if not categoria:
            raise ResourceNotFoundError(
                detail=f"Categoria não encontrada no id: {categoria_id}"
            )
        return categoria

    @staticmethod
    async def get_by_nome(db_session: AsyncSession, nome: str) -> CategoriaModel | None:
        stmt = select(CategoriaModel).where(
            func.lower(CategoriaModel.nome) == nome.strip().lower()
        )
        return (await db_session.execute(stmt)).scalars().first()
