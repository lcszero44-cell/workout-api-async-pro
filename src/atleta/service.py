from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.atleta.models import AtletaModel
from src.atleta.schemas import AtletaIn, AtletaUpdate, sanitize_cpf
from src.categorias.service import CategoriaService
from src.centro_treinamento.service import CentroTreinamentoService
from src.contrib.exceptions import DuplicateResourceError, ResourceNotFoundError


class AtletaService:
    """Camada de serviço assíncrona para regras de negócio e persistência de Atletas."""

    @staticmethod
    async def create(db_session: AsyncSession, atleta_in: AtletaIn) -> AtletaModel:
        categoria_nome = atleta_in.categoria.nome
        centro_nome = atleta_in.centro_treinamento.nome

        categoria = await CategoriaService.get_by_nome(db_session, categoria_nome)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A categoria '{categoria_nome}' não foi encontrada.",
            )

        centro_treinamento = await CentroTreinamentoService.get_by_nome(
            db_session, centro_nome
        )
        if not centro_treinamento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O centro de treinamento '{centro_nome}' não foi encontrado.",
            )

        atleta_data = atleta_in.model_dump(exclude={"categoria", "centro_treinamento"})
        atleta = AtletaModel(
            **atleta_data,
            created_at=datetime.now(timezone.utc),
            categoria_id=categoria.pk_id,
            centro_treinamento_id=centro_treinamento.pk_id,
        )

        db_session.add(atleta)
        try:
            await db_session.commit()
            await db_session.refresh(atleta, attribute_names=["categoria", "centro_treinamento"])
            return atleta
        except IntegrityError as exc:
            await db_session.rollback()
            raise DuplicateResourceError(
                detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}"
            ) from exc

    @staticmethod
    def get_all_query(
        nome: str | None = None,
        cpf: str | None = None,
    ) -> Select[tuple[AtletaModel]]:
        query = (
            select(AtletaModel)
            .options(
                selectinload(AtletaModel.categoria),
                selectinload(AtletaModel.centro_treinamento),
            )
            .order_by(AtletaModel.pk_id.asc())
        )

        if nome is not None and nome.strip():
            query = query.where(AtletaModel.nome.ilike(f"%{nome.strip()}%"))

        if cpf is not None and cpf.strip():
            cpf_sanitized = sanitize_cpf(cpf)
            query = query.where(AtletaModel.cpf == (cpf_sanitized or cpf.strip()))

        return query

    @staticmethod
    async def get_by_id(db_session: AsyncSession, atleta_id: UUID) -> AtletaModel:
        stmt = (
            select(AtletaModel)
            .options(
                selectinload(AtletaModel.categoria),
                selectinload(AtletaModel.centro_treinamento),
            )
            .where(AtletaModel.id == atleta_id)
        )
        atleta = (await db_session.execute(stmt)).scalars().first()
        if not atleta:
            raise ResourceNotFoundError(
                detail=f"Atleta não encontrado no id: {atleta_id}"
            )
        return atleta

    @staticmethod
    async def update(
        db_session: AsyncSession,
        atleta_id: UUID,
        atleta_up: AtletaUpdate,
    ) -> AtletaModel:
        atleta = await AtletaService.get_by_id(db_session, atleta_id)
        update_data = atleta_up.model_dump(exclude_unset=True)

        if "categoria" in update_data and atleta_up.categoria is not None:
            categoria = await CategoriaService.get_by_nome(
                db_session, atleta_up.categoria.nome
            )
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A categoria '{atleta_up.categoria.nome}' não foi encontrada.",
                )
            atleta.categoria_id = categoria.pk_id
            update_data.pop("categoria")

        if "centro_treinamento" in update_data and atleta_up.centro_treinamento is not None:
            centro = await CentroTreinamentoService.get_by_nome(
                db_session, atleta_up.centro_treinamento.nome
            )
            if not centro:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"O centro de treinamento '{atleta_up.centro_treinamento.nome}' "
                        "não foi encontrado."
                    ),
                )
            atleta.centro_treinamento_id = centro.pk_id
            update_data.pop("centro_treinamento")

        for field, value in update_data.items():
            setattr(atleta, field, value)

        try:
            await db_session.commit()
            await db_session.refresh(atleta, attribute_names=["categoria", "centro_treinamento"])
            return atleta
        except IntegrityError as exc:
            await db_session.rollback()
            cpf_conflict = atleta_up.cpf or atleta.cpf
            raise DuplicateResourceError(
                detail=f"Já existe um atleta cadastrado com o cpf: {cpf_conflict}"
            ) from exc

    @staticmethod
    async def delete(db_session: AsyncSession, atleta_id: UUID) -> None:
        atleta = await AtletaService.get_by_id(db_session, atleta_id)
        await db_session.delete(atleta)
        await db_session.commit()
