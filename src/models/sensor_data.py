from pydantic import BaseModel, Field
from datetime import datetime

class Viagem(BaseModel):
    data_inicio: datetime
    data_fim: datetime
    categoria: str
    local_inicio: str
    local_fim: str
    distancia: float = Field(..., ge=0)
    proposito: str = None
