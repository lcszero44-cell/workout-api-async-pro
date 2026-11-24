from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.contrib.models import BaseModel

if TYPE_CHECKING:
    from src.atleta.models import AtletaModel


class CategoriaModel(BaseModel):
    """Entidade ORM representando uma categoria de competição de CrossFit."""

    __tablename__ = "categorias"

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    atletas: Mapped[list["AtletaModel"]] = relationship(
        back_populates="categoria",
        lazy="selectin",
    )
