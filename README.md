# Desafio-Proxy-TDSOFT
# Proxy Interno Resiliente

Este projeto é a implementação de um serviço de proxy interno resiliente, desenvolvido como solução para o desafio "Proxy Interno". O objetivo principal é gerenciar o fluxo de requisições de múltiplos clientes internos para uma API externa que impõe um limite de taxa (rate limit) de 1 requisição por segundo.

O serviço utiliza uma fila interna e um scheduler para garantir que o limite nunca seja excedido, evitando penalidades e minimizando a latência para os clientes.

## Decisões de Design e Padrões Utilizados

A arquitetura do serviço foi construída sobre uma base sólida de padrões de projeto para garantir manutenibilidade, extensibilidade e resiliência.

* **Command**: Todas as requisições recebidas pela API são encapsuladas em objetos `ProxyRequestCommand`. Isso desacopla o receptor da requisição (a API) do executor, permitindo que as requisições sejam tratadas como unidades de trabalho que podem ser enfileiradas e gerenciadas.

* **Singleton**: A `RequestQueue` é implementada como um Singleton (instância única a nível de módulo). Isso garante que toda a aplicação compartilhe uma única fila centralizada, que é essencial para o controle global do rate limit.

* **Decorator**: Este padrão é o pilar da lógica de resiliência. A execução de um comando passa por uma pilha de decorators, onde cada um adiciona uma nova responsabilidade:
    * `CacheDecorator`: Adiciona uma camada de cache em memória para retornar respostas para requisições idênticas rapidamente, sem consumir a cota da API externa.
    * `CircuitBreakerDecorator`: Monitora falhas na comunicação com a API externa. Se um número configurável de falhas ocorrer, o circuito "abre", e o serviço para de tentar enviar requisições por um tempo, evitando sobrecarregar um serviço instável.
    * `HttpExecutor`: O executor base que efetivamente realiza a chamada externa.

* **Observer**: Utilizado para criar um sistema de observabilidade desacoplado. A `RequestQueue` notifica `Observers` sobre eventos importantes (ex: `enqueued`, `dropped`). Isso permite que componentes como o `StructuredLogger` e o `MetricsCollector` reajam a esses eventos sem que a fila precise conhecê-los diretamente.

* **Strategy (Conceitual)**: A arquitetura foi projetada para suportar o padrão Strategy para a política de enfileiramento. Embora a implementação atual use FIFO (`popleft`), a lógica pode ser facilmente extraída para uma interface `QueueingStrategy`, permitindo a implementação de políticas de Prioridade ou TTL, conforme exigido pelo desafio.

## Como Rodar

### Pré-requisitos
* Docker e Docker Compose
* (Alternativo) Python 3.9+ e `pip`

### Método 1: Usando Docker Compose (Recomendado)

Esta é a forma mais simples de subir a aplicação, com todas as suas dependências isoladas.

1.  Clone o repositório.
2.  Crie os arquivos `requirements.txt`, `Dockerfile` e `docker-compose.yml` na raiz do projeto.
3.  Execute o seguinte comando na raiz do projeto:
    ```bash
    docker-compose up --build
    ```
A aplicação estará rodando e acessível em `http://127.0.0.1:8000`.

### Método 2: Rodando Localmente

1.  Clone o repositório e navegue até ele.
2.  Crie e ative um ambiente virtual:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Inicie a aplicação:
    ```bash
    python proxy_service/main.py
    ```

### Variáveis de Ambiente
O serviço pode ser configurado através de variáveis de ambiente (atualmente definidas no `docker-compose.yml`). No futuro, o código pode ser adaptado para lê-las.

* `QUEUE_MAX_SIZE`: Tamanho máximo da fila de requisições. (Padrão: 100)
* `CACHE_TTL_SECONDS`: Tempo de vida (em segundos) de um item no cache. (Padrão: 60)
* `CIRCUIT_BREAKER_FAILURE_THRESHOLD`: Número de falhas consecutivas para abrir o circuito. (Padrão: 3)

## Endpoints e Exemplos de Uso

### Documentação Interativa (Swagger UI)

A forma mais fácil de interagir com a API é através da documentação gerada automaticamente. Acesse no seu navegador:

**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

Lá você pode visualizar todos os endpoints, seus parâmetros e executar requisições de teste.

### Endpoints

| Método | Endpoint  | Descrição                                                                      |
|--------|-----------|--------------------------------------------------------------------------------|
| `GET`  | `/score/` | Enfileira uma consulta de score para processamento. Requer `name` e `cpf`.     |
| `GET`  | `/health` | Verifica a saúde e a disponibilidade do serviço.                               |

### Exemplos com `curl`

#### 1. Consulta de Score Simples
```bash
curl -X GET "[http://127.0.0.1:8000/score/?name=Joao%20Silva&cpf=12345678900](http://127.0.0.1:8000/score/?name=Joao%20Silva&cpf=12345678900)"
