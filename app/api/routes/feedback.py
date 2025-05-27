from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas.feedback_schema import FeedbackRequest, FeedbackResponse
from app.core.feedback_service import FeedbackService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/feedback", response_model=FeedbackResponse)
def enviar_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        FeedbackService.salvar_feedback(
            analise_id=payload.analise_id,
            avaliacao=payload.avaliacao,
            comentario=payload.comentario,
            db=db
        )
        return FeedbackResponse(status="ok", message="Feedback registrado com sucesso.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))