# proxy_service/server.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from components import request_queue, ProxyRequestCommand 

# Cria a aplicação FastAPI
app = FastAPI(
    title="Proxy Interno para Score API",
    description="Este serviço atua como um proxy resiliente para a API score.hsborges.dev, gerenciando o rate limit.",
    version="1.0.0",
)

@app.get(
    "/score/", 
    tags=["Score"],
    summary="Enfileira uma consulta de score",
    description="Aceita os parâmetros `name` e `cpf`, encapsula-os em um comando e os adiciona à fila de processamento do proxy.",
    status_code=status.HTTP_202_ACCEPTED
)
def proxy_score(name: str, cpf: str):
    """
    Endpoint principal que simula a API externa.
    - **name**: Nome do cliente.
    - **cpf**: CPF do cliente.
    """
    payload = {"name": name, "cpf": cpf}
    print(f"WEB SERVER -> Requisição recebida para /score/ com payload: {payload}")

    command = ProxyRequestCommand(payload=payload)
    success = request_queue.add(command)

    if success:
        return {"status": "Request accepted and queued for processing"}
    else:
        # Retorna uma resposta 503 Service Unavailable se a fila estiver cheia
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "Service is busy, queue is full. Please try again later."},
        )

@app.get(
    "/health", 
    tags=["Monitoring"],
    summary="Verifica a saúde do serviço"
)
def health_check():
    """
    Atende ao requisito RF3: Expor GET /health.
    """
    return {"status": "ok"}
