from langchain.tools import tool
from app.database.session import SessionLocal
from app.models import usuario as usuario_model, conexao as conexao_model
from sqlalchemy.orm import Session
from sqlalchemy import func

@tool
def estatisticas_tool(android_id: str) -> dict:
    """
    Retorna estatísticas simples de conexões do usuário como dicionário.
    """
    return _get_estatisticas_usuario_com_db(android_id)

def _get_estatisticas_usuario_com_db(android_id: str) -> dict:
    db: Session = SessionLocal()
    try:
        usuario = db.query(usuario_model.Usuario).filter_by(android_id=android_id).first()
        if not usuario:
            return {"mensagem": "Usuário não encontrado."}

        total_conexoes = db.query(conexao_model.ConexaoCapturada)\
                            .filter_by(usuario_id=usuario.id).count()

        porta_mais_usada = db.query(conexao_model.ConexaoCapturada.porta_destino, func.count())\
                              .filter_by(usuario_id=usuario.id)\
                              .group_by(conexao_model.ConexaoCapturada.porta_destino)\
                              .order_by(func.count().desc())\
                              .first()

        if total_conexoes == 0:
            return {"mensagem": "Nenhuma estatística disponível."}

        return {
            "total_conexoes": total_conexoes,
            "porta_mais_usada": porta_mais_usada[0] if porta_mais_usada else None
        }
    finally:
        db.close()
