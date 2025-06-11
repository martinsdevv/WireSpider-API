# Revisão das tools para uso correto com Gemini + LangChain

from langchain.tools import tool
import requests
import os
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models import usuario as usuario_model, conexao as conexao_model
from sqlalchemy import func

# Tool: Verifica reputação de IP com contexto
@tool
def ip_tool(ip_destino: str) -> str:
    """
    Usa o AbuseIPDB para verificar se um IP tem histórico de abusos. 
    Retorna país, tipo de uso (residencial, datacenter, etc) e índice de abuso (0-100).
    
    Use isso para ajudar a avaliar se um IP é confiável.
    """
    ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip_destino,
        "maxAgeInDays": 90
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code != 200:
        return f"Erro ao verificar IP: {data.get('errors', [{'detail': 'Erro desconhecido'}])[0]['detail']}"

    abuso = data["data"].get("abuseConfidenceScore", 0)
    pais = data["data"].get("countryCode", "N/A")
    uso = data["data"].get("usageType", "N/A")

    return (
        f"IP {ip_destino} — País: {pais}, Tipo de uso: {uso}, Índice de abuso: {abuso}/100."
        " Avalie negativamente se abuso > 50."
    )


# Tool: Estatísticas do usuário
@tool
def estatisticas_tool(android_id: str) -> dict:
    """
    Gera estatísticas de uso de rede do usuário.
    Inclui total de conexões e portas mais usadas para comparar comportamento atual.
    """
    db: Session = SessionLocal()
    try:
        usuario = db.query(usuario_model.Usuario).filter_by(android_id=android_id).first()
        if not usuario:
            return {"mensagem": "Usuário não encontrado."}

        total_conexoes = db.query(conexao_model.ConexaoCapturada)\
            .filter_by(usuario_id=usuario.id).count()

        portas_freq = db.query(conexao_model.ConexaoCapturada.porta_destino, func.count())\
            .filter_by(usuario_id=usuario.id)\
            .group_by(conexao_model.ConexaoCapturada.porta_destino)\
            .order_by(func.count().desc())\
            .limit(5).all()

        return {
            "total_conexoes": total_conexoes,
            "portas_frequentes": [str(p[0]) for p in portas_freq]
        }
    finally:
        db.close()


# Tool: Histórico de conexões
@tool
def historico_tool(android_id: str) -> str:
    """
    Lista as últimas 20 conexões feitas pelo usuário.
    Serve para entender padrões e comparar com comportamento atual.
    """
    db: Session = SessionLocal()
    try:
        usuario = db.query(usuario_model.Usuario).filter_by(android_id=android_id).first()
        if not usuario:
            return "Usuário não encontrado."

        conexoes = db.query(conexao_model.ConexaoCapturada)\
            .filter_by(usuario_id=usuario.id)\
            .order_by(conexao_model.ConexaoCapturada.timestamp.desc())\
            .limit(20).all()

        return "\n".join([
            f"{c.timestamp} - {c.ip_origem}:{c.porta_origem} -> {c.ip_destino}:{c.porta_destino} ({c.protocolo})"
            for c in conexoes
        ])
    finally:
        db.close()


# Tool: Valida combinação de protocolo e porta
@tool
def protocolo_tool(protocolo: str, porta: int) -> str:
    """
    Verifica se a porta está correta para o protocolo.
    Pode indicar configuração errada ou tentativa de camuflagem de tráfego.
    """
    padroes = {
        ("HTTPS", 443): "HTTPS na porta 443 — padrão seguro.",
        ("HTTP", 80): "HTTP na porta 80 — comum, mas sem criptografia.",
        ("DNS", 53): "DNS na porta 53 — padrão normal.",
        ("FTP", 21): "FTP na porta 21 — conexão insegura, monitorar."  
    }
    return padroes.get((protocolo.upper(), porta), f"Protocolo {protocolo} na porta {porta} — verificar se é esperado.")
