from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas.analise_schema import AnaliseRequest, AnaliseResponse
from app.models.analise import AnaliseIA
from app.core.mcp_service import MCPService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/analise", response_model=AnaliseResponse)
def analisar_conexao(request: AnaliseRequest, db: Session = Depends(get_db)):
    return MCPService.analisar(request, db)

@router.get("/analise/{analise_id}", response_model=AnaliseResponse)
def obter_analise(analise_id: int, db: Session = Depends(get_db)):
    analise = db.query(AnaliseIA).filter_by(id=analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")

    # Monta o objeto de resposta
    resposta = AnaliseResponse(
        analise_id=analise.id,
        risco=analise.risco_detectado,
        comportamento_suspeito=analise.comportamento_suspeito,
        recomendacao=analise.recomendacao,
        confianca=analise.score_confianca
    )
    return resposta

