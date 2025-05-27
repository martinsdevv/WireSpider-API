import requests
from langchain.tools import tool
import os

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")

@tool
def ip_tool(ip_destino: str) -> str:
    """
    Usa AbuseIPDB para verificar reputação de um IP.
    """
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
    
    abuse_confidence = data["data"]["abuseConfidenceScore"]
    country = data["data"].get("countryCode", "N/A")
    usage_type = data["data"].get("usageType", "N/A")
    
    return (
        f"IP: {ip_destino} — País: {country}, Uso: {usage_type}, "
        f"Índice de abuso: {abuse_confidence}/100. "
        "Avaliar necessidade de bloqueio se índice for alto."
    )
