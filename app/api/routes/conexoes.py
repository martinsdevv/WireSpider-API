from fastapi import APIRouter, Depends, HTTPException, Query
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
def listar_conexoes(
    captura_id: str,
    limit: int = Query(default=20, ge=1),
    db: Session = Depends(get_db)
):
    # Busca conexões do captura_id fornecido, ordenadas pelo timestamp desc
    conexoes = db.query(conexao_model.ConexaoCapturada)\
        .filter_by(captura_id=captura_id)\
        .order_by(conexao_model.ConexaoCapturada.timestamp.desc())\
        .limit(limit)\
        .all()

    return conexoes
