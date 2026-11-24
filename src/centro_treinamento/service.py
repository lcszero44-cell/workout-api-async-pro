from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.centro_treinamento.models import CentroTreinamentoModel
from src.centro_treinamento.schemas import CentroTreinamentoIn
from src.contrib.exceptions import DuplicateResourceError, ResourceNotFoundError


class CentroTreinamentoService:
    """Camada de serviço assíncrona para operações de domínio de Centros de Treinamento."""

    @staticmethod
    async def create(
        db_session: AsyncSession,
        ct_in: CentroTreinamentoIn,
    ) -> CentroTreinamentoModel:
        centro_treinamento = CentroTreinamentoModel(**ct_in.model_dump())
        db_session.add(centro_treinamento)
        try:
            await db_session.commit()
            await db_session.refresh(centro_treinamento)
            return centro_treinamento
        except IntegrityError as exc:
            await db_session.rollback()
            raise DuplicateResourceError(
                detail=f"Já existe um centro de treinamento cadastrado com o nome: {ct_in.nome}"
            ) from exc

    @staticmethod
    def get_all_query() -> Select[tuple[CentroTreinamentoModel]]:
        return select(CentroTreinamentoModel).order_by(CentroTreinamentoModel.pk_id.asc())

    @staticmethod
    async def get_by_id(
        db_session: AsyncSession,
        centro_treinamento_id: UUID,
    ) -> CentroTreinamentoModel:
        stmt = select(CentroTreinamentoModel).where(
            CentroTreinamentoModel.id == centro_treinamento_id
        )
        centro = (await db_session.execute(stmt)).scalars().first()
        if not centro:
            raise ResourceNotFoundError(
                detail=f"Centro de treinamento não encontrado no id: {centro_treinamento_id}"
            )
        return centro

    @staticmethod
    async def get_by_nome(
        db_session: AsyncSession,
        nome: str,
    ) -> CentroTreinamentoModel | None:
        stmt = select(CentroTreinamentoModel).where(
            func.lower(CentroTreinamentoModel.nome) == nome.strip().lower()
        )
        return (await db_session.execute(stmt)).scalars().first()
