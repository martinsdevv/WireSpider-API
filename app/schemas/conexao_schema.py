from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ConexaoBase(BaseModel):
    timestamp: datetime
    ip_origem: str
    ip_destino: str
    porta_origem: int
    porta_destino: int
    protocolo: str
    tamanho: int
    dns_requisitado: Optional[str] = None

class ConexoesRequest(BaseModel):
    android_id: str
    conexoes: List[ConexaoBase]

class ConexaoResponse(ConexaoBase):
    id: int
    captura_id: str

    class Config:
        orm_mode = True
