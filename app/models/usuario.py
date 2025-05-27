from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    android_id = Column(String, unique=True, index=True, nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

    conexoes = relationship("ConexaoCapturada", back_populates="usuario")
