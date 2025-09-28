# proxy_service/main.py

import uvicorn
from components import (
    request_queue, 
    Scheduler, 
    HttpExecutor, 
    CircuitBreakerDecorator, 
    CacheDecorator
)
from observers import StructuredLogger, MetricsCollector
from server import app as fast_api_app

def main():
    print("Iniciando o serviço de Proxy Interno...")

    # 1. Instanciar e anexar Observers
    logger = StructuredLogger()
    metrics = MetricsCollector()
    request_queue.attach(logger)
    request_queue.attach(metrics)

    # 2. Montar a pilha de executores (Decorators)
    base_executor = HttpExecutor()
    executor_com_resiliencia = CircuitBreakerDecorator(base_executor)
    executor_final = CacheDecorator(executor_com_resiliencia)

    # 3. Iniciar o Scheduler em uma thread separada
    scheduler = Scheduler(request_queue, executor_final)
    scheduler.start()
    print("Scheduler iniciado em background.")

    # 4. Iniciar o servidor web FastAPI usando Uvicorn
    print("Iniciando o servidor web FastAPI...")
    print("Acesse a documentação interativa em http://127.0.0.1:8000/docs")
    
    # Uvicorn roda a aplicação FastAPI
    uvicorn.run(fast_api_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
