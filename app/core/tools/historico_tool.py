from langchain.tools import tool
from app.models.conexao import ConexaoCapturada
from sqlalchemy.orm import Session

@tool
def historico_tool(android_id: str) -> str:
    """
    Retorna as últimas 20 conexões do usuário, formatadas como texto.
    """
    return _get_ultimas_conexoes_com_db(android_id)

def _get_ultimas_conexoes_com_db(android_id: str) -> str:
    db: Session = SessionLocal()
    try:
        from app.models import usuario as usuario_model, conexao as conexao_model

        usuario = db.query(usuario_model.Usuario).filter_by(android_id=android_id).first()
        if not usuario:
            return "Usuário não encontrado."

        conexoes = db.query(conexao_model.ConexaoCapturada)\
                    .filter_by(usuario_id=usuario.id)\
                    .order_by(conexao_model.ConexaoCapturada.timestamp.desc())\
                    .limit(20).all()
        if not conexoes:
            return "Nenhuma conexão encontrada."

        return "\n".join([
            f"{c.timestamp} - {c.ip_origem}:{c.porta_origem} -> {c.ip_destino}:{c.porta_destino} ({c.protocolo})"
            for c in conexoes
        ])
    finally:
        db.close()

