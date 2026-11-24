from datetime import datetime
from typing import Annotated

from pydantic import UUID4, BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Strict Pydantic v2 base schema with ORM attribute mapping enabled."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class OutMixin(BaseSchema):
    """Standard metadata mixin for detailed resource responses."""

    id: Annotated[UUID4, Field(description="Identificador único universal (UUID4)")]
    created_at: Annotated[datetime, Field(description="Data e hora de criação (UTC)")]
