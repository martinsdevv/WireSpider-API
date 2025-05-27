from pydantic import BaseModel, Field
from typing import Optional

class FeedbackRequest(BaseModel):
    analise_id: int = Field(..., example=123)
    avaliacao: str = Field(..., example="correto")  # "correto" ou "incorreto"
    comentario: Optional[str] = Field(None, example="A análise bateu exatamente com o esperado!")

class FeedbackResponse(BaseModel):
    status: str
    message: str
