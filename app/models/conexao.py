from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ConexaoCapturada(Base):
    __tablename__ = "conexoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    captura_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    ip_origem = Column(String, nullable=False)
    ip_destino = Column(String, nullable=False)
    porta_origem = Column(Integer, nullable=False)
    porta_destino = Column(Integer, nullable=False)
    protocolo = Column(String, nullable=False)
    tamanho = Column(Integer, nullable=False)
    dns_requisitado = Column(String, nullable=True)

    usuario = relationship("Usuario", back_populates="conexoes")
    analise = relationship("AnaliseIA", back_populates="conexao", uselist=False)
