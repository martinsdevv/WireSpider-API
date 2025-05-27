from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Union, List

class AnaliseRequest(BaseModel):
    android_id: str = Field(..., example="abc123xyz")
    conexao_id: int
    captura_id: str


class AnaliseResponse(BaseModel):
    analise_id: int
    risco: str
    comportamento_suspeito: Union[str, List[str]]
    recomendacao: Union[str, List[str]]
    confianca: float
