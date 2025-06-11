from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.mcp_tools import historico_tool, estatisticas_tool, ip_tool, protocolo_tool
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
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

        # Prompt com espaço reservado para histórico do agente
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Você é um analista de cibersegurança. Responda em português. Use ferramentas quando necessário."
            ),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Criação do agente com suporte a funções (tools)
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def analisar(self, input_data: str):
        response = self.executor.invoke({"input": input_data})
        return response["output"]

    def obter_reputacao_ip(self, ip_destino: str):
        return ip_tool.run(ip_destino)

    def obter_estatisticas_usuario(self, android_id: str):
        return estatisticas_tool.run(android_id)
