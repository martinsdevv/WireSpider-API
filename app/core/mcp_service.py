from sqlalchemy.orm import Session
from app.models import usuario as usuario_model
from app.models import conexao as conexao_model
from app.models import analise as analise_model
from app.schemas.analise_schema import AnaliseRequest, AnaliseResponse
from app.core.langchain_service import LangChainService
import json
import re
import logging
import httpx

class MCPService:

    @staticmethod
    def extrair_json(texto: str):
        """
        Extrai o primeiro bloco JSON válido de um texto.
        """
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            json_str = match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                raise Exception(f"JSON inválido:\n{json_str}")
        raise Exception(f"Nenhum JSON encontrado:\n{texto}")

    @staticmethod
    def calcular_confianca(conexao, reputacao_ip, estatisticas_usuario):
        """
        Calcula o índice de confiança da rede baseado em:
        - reputação do IP (abuseConfidenceScore real)
        - protocolo e porta
        - frequência de uso (histórico do usuário)
        """

        # 1️⃣ Reputação do IP
        match_abuse = re.search(r'Índice de abuso: (\d+)/100', reputacao_ip)
        if match_abuse:
            abuse_score = int(match_abuse.group(1))
            score_ip = 1 - (abuse_score / 100)
        else:
            # Se não conseguiu extrair, assume neutro
            score_ip = 0.5

        # 2️⃣ Protocolo e porta
        protocolo_porta_segura = {
            ("HTTPS", 443),
            ("HTTP", 80),
            ("DNS", 53),
            ("FTP", 21)
        }
        if (conexao.protocolo.upper(), conexao.porta_destino) in protocolo_porta_segura:
            score_protocolo = 0.9
        else:
            score_protocolo = 0.5

        # 3️⃣ Histórico do usuário
        portas_frequentes = estatisticas_usuario.get("portas_frequentes", [])
        if str(conexao.porta_destino) in portas_frequentes:
            score_historico = 0.9
        else:
            score_historico = 0.6

        # 4️⃣ Combinação final (ponderada)
        confianca_final = (score_ip * 0.4) + (score_protocolo * 0.4) + (score_historico * 0.2)
        confianca_final = round(confianca_final, 2)

        # Log para debug
        print(f"[DEBUG] Cálculo de confiança: score_ip={score_ip}, "
            f"score_protocolo={score_protocolo}, "
            f"score_historico={score_historico}, "
            f"confianca_final={confianca_final}")

        return confianca_final



    @staticmethod
    def analisar(request: AnaliseRequest, db: Session) -> AnaliseResponse:
        usuario = db.query(usuario_model.Usuario).filter_by(android_id=request.android_id).first()
        if not usuario:
            raise Exception("Usuário não encontrado")

        conexao = db.query(conexao_model.ConexaoCapturada)\
            .filter_by(id=request.conexao_id, usuario_id=usuario.id, captura_id=request.captura_id)\
            .first()
        if not conexao:
            raise Exception("Conexão não encontrada para o usuário e captura_id informados")

        # Chama LangChainService
        langchain_service = LangChainService(db=db, usuario_id=usuario.id)
        prompt_input = (
            f"Analise a conexão do usuário:\n"
            f"IP origem: {conexao.ip_origem}\n"
            f"IP destino: {conexao.ip_destino}\n"
            f"Porta origem: {conexao.porta_origem}\n"
            f"Porta destino: {conexao.porta_destino}\n"
            f"Protocolo: {conexao.protocolo}\n"
            f"Tamanho: {conexao.tamanho}\n"
            f"DNS requisitado: {conexao.dns_requisitado}\n"
            f"Timestamp: {conexao.timestamp}\n\n"
            f"Responda apenas em JSON com as chaves: risco, comportamento_suspeito, recomendacao."
        )
        resposta_texto = langchain_service.analisar(prompt_input)
        resposta_ia = MCPService.extrair_json(resposta_texto)

        # Obter reputação do IP via tool
        reputacao_ip = langchain_service.obter_reputacao_ip(conexao.ip_destino)
        # Obter estatísticas do usuário via tool
        estatisticas_usuario = langchain_service.obter_estatisticas_usuario(usuario.android_id)

        # Calcular a confiança
        confianca = MCPService.calcular_confianca(conexao, reputacao_ip, estatisticas_usuario)
        ip_loc = buscar_geolocalizacao(conexao.ip_destino)

        # Salvar a análise
        analise = analise_model.AnaliseIA(
            conexao_id=conexao.id,
            risco_detectado=resposta_ia["risco"],
            comportamento_suspeito=resposta_ia["comportamento_suspeito"],
            recomendacao=resposta_ia["recomendacao"],
            score_confianca=confianca,
            modelo_utilizado="LangChain + Gemini"
        )
        db.add(analise)
        db.commit()

        # Retornar a resposta ao front
        return AnaliseResponse(
            analise_id=analise.id,
            risco=resposta_ia["risco"],
            comportamento_suspeito=resposta_ia["comportamento_suspeito"],
            recomendacao=resposta_ia["recomendacao"],
            confianca=confianca,
            ip_loc=ip_loc
        )


def buscar_geolocalizacao(ip: str) -> str:
    try:
        response = httpx.get(f"https://ipwho.is/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return f"{data['latitude']},{data['longitude']}"
    except Exception as e:
        print(f"[GeoIP] Erro ao buscar localização de {ip}: {e}")
    return ""