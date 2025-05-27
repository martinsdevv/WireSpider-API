from langchain.tools import tool

@tool
def protocolo_tool(protocolo: str, porta: int) -> str:
    """
    Valida se o protocolo e a porta estão coerentes.
    """
    if protocolo.upper() == "HTTPS" and porta == 443:
        return "HTTPS na porta 443 — padrão seguro."
    if protocolo.upper() == "HTTP" and porta == 80:
        return "HTTP na porta 80 — normal, mas sem criptografia."
    if protocolo.upper() == "DNS" and porta == 53:
        return "DNS na porta 53 — normal."
    if protocolo.upper() == "FTP" and porta == 21:
        return "FTP na porta 21 — monitorar, pois FTP não é seguro."
    return f"Protocolo {protocolo} na porta {porta} — verificar se é esperado."
