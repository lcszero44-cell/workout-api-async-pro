from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.contrib.models import BaseModel

if TYPE_CHECKING:
    from src.atleta.models import AtletaModel


class CentroTreinamentoModel(BaseModel):
    """Entidade ORM representando um Centro de Treinamento (Box de CrossFit)."""

    __tablename__ = "centros_treinamento"

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    endereco: Mapped[str] = mapped_column(String(100), nullable=False)
    proprietario: Mapped[str] = mapped_column(String(50), nullable=False)

    atletas: Mapped[list["AtletaModel"]] = relationship(
        back_populates="centro_treinamento",
        lazy="selectin",
    )
