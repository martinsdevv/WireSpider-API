from sqlalchemy.orm import Session
from app.models import usuario as usuario_model
from app.models import conexao as conexao_model
from app.models import analise as analise_model
from app.schemas.analise_schema import AnaliseRequest, AnaliseResponse
from app.core.langchain_service import LangChainService
import json
import re
import httpx

class MCPService:

    @staticmethod
    def extrair_json(texto: str):
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
        match_abuse = re.search(r'\u00cdndice de abuso: (\d+)/100', reputacao_ip)
        score_ip = 1 - (int(match_abuse.group(1)) / 100) if match_abuse else 0.5

        protocolo_porta_segura = {("HTTPS", 443), ("HTTP", 80), ("DNS", 53), ("FTP", 21)}
        score_protocolo = 0.9 if (conexao.protocolo.upper(), conexao.porta_destino) in protocolo_porta_segura else 0.5

        portas_frequentes = estatisticas_usuario.get("portas_frequentes", [])
        score_historico = 0.9 if str(conexao.porta_destino) in portas_frequentes else 0.6

        confianca_final = round((score_ip * 0.4) + (score_protocolo * 0.4) + (score_historico * 0.2), 2)

        print(f"[DEBUG] Confianca: ip={score_ip}, protocolo={score_protocolo}, historico={score_historico}, final={confianca_final}")
        return confianca_final

    @staticmethod
    def analisar(request: AnaliseRequest, db: Session) -> AnaliseResponse:
        usuario = db.query(usuario_model.Usuario).filter_by(android_id=request.android_id).first()
        if not usuario:
            raise Exception("Usuário não encontrado")

        conexao = db.query(conexao_model.ConexaoCapturada).filter_by(
            id=request.conexao_id, usuario_id=usuario.id, captura_id=request.captura_id).first()
        if not conexao:
            raise Exception("Conexão não encontrada")

        contexto_sistema = (
            "⚠️ CONTEXTO IMPORTANTE:\n"
            "Este tráfego foi capturado por um app Android chamado WireSpider.\n"
            "O app utiliza uma VPN local (IP 10.0.0.2) e um proxy HTTP local (127.0.0.1:8888).\n"
            "Esses IPs fazem parte da infraestrutura do app e não representam comportamento malicioso.\n"
        )

        langchain_service = LangChainService(db=db, usuario_id=usuario.id)
        prompt_input = contexto_sistema + "\n\n" + (
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

        reputacao_ip = langchain_service.obter_reputacao_ip(conexao.ip_destino)
        estatisticas_usuario = langchain_service.obter_estatisticas_usuario(usuario.android_id)
        confianca = MCPService.calcular_confianca(conexao, reputacao_ip, estatisticas_usuario)
        ip_loc = MCPService.buscar_geolocalizacao(conexao.ip_destino)

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

        return AnaliseResponse(
            analise_id=analise.id,
            risco=resposta_ia["risco"],
            comportamento_suspeito=resposta_ia["comportamento_suspeito"],
            recomendacao=resposta_ia["recomendacao"],
            confianca=confianca,
            ip_loc=ip_loc
        )

    @staticmethod
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
