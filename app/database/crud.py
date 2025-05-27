from sqlalchemy.orm import Session
from app.models import usuario as usuario_model, conexao as conexao_model
from app.schemas import conexao_schema
from datetime import datetime
from typing import List

def get_or_create_usuario(db: Session, android_id: str) -> usuario_model.Usuario:
    usuario = db.query(usuario_model.Usuario).filter_by(android_id=android_id).first()
    if usuario is None:
        usuario = usuario_model.Usuario(android_id=android_id)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario

def salvar_conexoes(db: Session, usuario_id: int, conexoes: List[conexao_schema.ConexaoBase], captura_id: int):
    for c in conexoes:
        conexao = conexao_model.ConexaoCapturada(
            usuario_id=usuario_id,
            captura_id=captura_id,
            timestamp=c.timestamp or datetime.utcnow(),
            ip_origem=c.ip_origem,
            ip_destino=c.ip_destino,
            porta_origem=c.porta_origem,
            porta_destino=c.porta_destino,
            protocolo=c.protocolo,
            tamanho=c.tamanho,
            dns_requisitado=c.dns_requisitado
        )
        db.add(conexao)
    db.commit()
