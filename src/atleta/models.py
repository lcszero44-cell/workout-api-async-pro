from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.contrib.models import BaseModel

if TYPE_CHECKING:
    from src.categorias.models import CategoriaModel
    from src.centro_treinamento.models import CentroTreinamentoModel


class AtletaModel(BaseModel):
    """Entidade ORM representando um Atleta de CrossFit."""

    __tablename__ = "atletas"

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    idade: Mapped[int] = mapped_column(Integer, nullable=False)
    peso: Mapped[float] = mapped_column(Float, nullable=False)
    altura: Mapped[float] = mapped_column(Float, nullable=False)
    sexo: Mapped[str] = mapped_column(String(1), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.pk_id", ondelete="RESTRICT"),
        nullable=False,
    )
    categoria: Mapped["CategoriaModel"] = relationship(
        back_populates="atletas",
        lazy="selectin",
    )

    centro_treinamento_id: Mapped[int] = mapped_column(
        ForeignKey("centros_treinamento.pk_id", ondelete="RESTRICT"),
        nullable=False,
    )
    centro_treinamento: Mapped["CentroTreinamentoModel"] = relationship(
        back_populates="atletas",
        lazy="selectin",
    )
