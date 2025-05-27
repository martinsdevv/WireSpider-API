from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analise, conexoes, feedback
from app.models.base import Base
from app.database.session import engine

import uvicorn

# Inicializa a aplicação
app = FastAPI(
    title="WireSpider API",
    version="1.0.0",
    description="API de análise de tráfego com IA",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (permitir chamadas do app mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # você pode restringir isso depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar as rotas
app.include_router(analise.router, prefix="")
app.include_router(conexoes.router, prefix="")
app.include_router(feedback.router, prefix="")

# Criar as tabelas automaticamente (opcional em produção)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
