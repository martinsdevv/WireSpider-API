from app.models import feedback as feedback_model, analise as analise_model
from sqlalchemy.orm import Session

class FeedbackService:

    @staticmethod
    def salvar_feedback(analise_id: int, avaliacao: str, comentario: str, db: Session):
        # Valida se análise existe
        analise = db.query(analise_model.AnaliseIA).filter_by(id=analise_id).first()
        if not analise:
            raise Exception("Análise não encontrada para o ID fornecido.")

        feedback = feedback_model.FeedbackUsuario(
            analise_id=analise_id,
            avaliacao=avaliacao,
            comentario=comentario
        )
        db.add(feedback)
        db.commit()
        return feedback