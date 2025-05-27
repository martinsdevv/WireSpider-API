from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import SessionLocal
from app.database import crud
from app.models import usuario as usuario_model, conexao as conexao_model
from app.schemas import conexao_schema
from typing import List
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/conexoes")
def receber_conexoes(payload: conexao_schema.ConexoesRequest, db: Session = Depends(get_db)):
    usuario = crud.get_or_create_usuario(db, payload.android_id)
    captura_id = str(uuid.uuid4())
    crud.salvar_conexoes(db, usuario.id, payload.conexoes, captura_id)

    return {"status": "ok", "captura_id": captura_id}

@router.get("/conexoes", response_model=List[conexao_schema.ConexaoResponse])
def listar_ultimas_conexoes(android_id: str, db: Session = Depends(get_db)):
    usuario = db.query(usuario_model.Usuario).filter_by(android_id=android_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Busca o captura_id mais recente (pela maior data de timestamp)
    subquery = db.query(
        conexao_model.ConexaoCapturada.captura_id,
        func.max(conexao_model.ConexaoCapturada.timestamp).label("max_timestamp")
    ).filter(
        conexao_model.ConexaoCapturada.usuario_id == usuario.id
    ).group_by(
        conexao_model.ConexaoCapturada.captura_id
    ).order_by(
        func.max(conexao_model.ConexaoCapturada.timestamp).desc()
    ).limit(1).subquery()

    captura_id_mais_recente = db.query(subquery.c.captura_id).scalar()

    # Busca conexões desse captura_id
    conexoes = db.query(conexao_model.ConexaoCapturada)\
        .filter_by(captura_id=captura_id_mais_recente)\
        .all()

    return conexoes
