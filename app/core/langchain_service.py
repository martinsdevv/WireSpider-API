from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.tools.historico_tool import historico_tool
from app.core.tools.estatisticas_tool import estatisticas_tool
from app.core.tools.ip_tool import ip_tool
from app.core.tools.protocolo_tool import protocolo_tool
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder
)


class LangChainService:

    def __init__(self, db, usuario_id):
        self.db = db
        self.usuario_id = usuario_id

        # Inicializa o modelo Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.2,
            convert_system_message_to_human=True
        )

        # Inicializa as tools
        self.tools = [
            historico_tool,
            estatisticas_tool,
            ip_tool,
            protocolo_tool,
        ]

        # Monta o prompt (inicial)
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("Você é um analista de cibersegurança. Responda em português."),
            HumanMessagePromptTemplate.from_template("{input}"),
            AIMessagePromptTemplate.from_template("{agent_scratchpad}")
        ])

        # Cria o agente
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # Executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True  # Para debug
        )

    def analisar(self, input_data: str):
        response = self.executor.invoke({"input": input_data})
        return response["output"]

    def obter_reputacao_ip(self, ip_destino: str):
        """
        Chama diretamente a tool de reputação de IP.
        """
        return ip_tool.run(ip_destino)

    def obter_estatisticas_usuario(self, android_id: str):
        """
        Chama diretamente a tool de estatísticas do usuário.
        """
        return estatisticas_tool.run(android_id)
