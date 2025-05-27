from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class AnaliseIA(Base):
    __tablename__ = "analises"

    id = Column(Integer, primary_key=True, index=True)
    conexao_id = Column(Integer, ForeignKey("conexoes.id"), nullable=False)
    risco_detectado = Column(String, nullable=False)
    comportamento_suspeito = Column(String, nullable=False)
    recomendacao = Column(String, nullable=False)
    score_confianca = Column(Float, nullable=False)
    modelo_utilizado = Column(String, nullable=False)

    conexao = relationship("ConexaoCapturada", back_populates="analise")
    # feedbacks = relationship("FeedbackUsuario", back_populates="analise")
