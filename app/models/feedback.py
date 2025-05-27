from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class FeedbackUsuario(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    analise_id = Column(Integer, ForeignKey("analises.id"), nullable=False)
    avaliacao = Column(String, nullable=False)  # "correto" / "incorreto"
    comentario = Column(String, nullable=True)

    analise = relationship("AnaliseIA", back_populates="feedbacks")
