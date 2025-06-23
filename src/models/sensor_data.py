# src/models/sensor_data.py (Sem alterações)

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Viagem(BaseModel):  # Este é o modelo Pydantic
    data_inicio: datetime
    data_fim: datetime
    categoria: str
    local_inicio: str
    local_fim: str
    distancia: float = Field(..., ge=0)
    proposito: Optional[str] = None
