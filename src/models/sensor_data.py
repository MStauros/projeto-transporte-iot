from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Viagem(BaseModel):
    data_inicio: datetime
    data_fim: datetime
    categoria: str
    local_inicio: str
    local_fim: str
    distancia: float = Field(..., ge=0)
    proposito: Optional[str] = None
