# proxy_service/components.py

import time
import threading
import json
from collections import deque
from abc import ABC, abstractmethod
from patterns import Command, Subject

# --- Padrão Singleton ---
class RequestQueue(Subject):
    def __init__(self, max_size: int = 100):
        super().__init__()
        self._commands = deque()
        self.max_size = max_size

    def add(self, command: Command):
        if len(self._commands) < self.max_size:
            self._commands.append(command)
            self.notify("enqueued", command=command, queue_size=len(self._commands))
            return True
        else:
            self.notify("dropped", reason="queue_full", command=command)
            return False

    def __iter__(self):
        while self._commands:
            yield self._commands.popleft()

request_queue = RequestQueue()


# --- Padrão Decorator para Execução ---

class Executor(ABC):
    """Interface para os executores de Command."""
    @abstractmethod
    def execute(self, command: Command):
        pass

class HttpExecutor(Executor):
    """Executor base que realiza a chamada HTTP."""
    def execute(self, command: Command):
        print(f"EXECUTING -> Chamando API externa para o comando: {command}")
        time.sleep(0.2)
        # O método do comando agora retorna um "resultado" para ser cacheado
        return command.execute()

class CacheDecorator(Executor):
    """Decorator que adiciona uma camada de cache em memória."""
    def __init__(self, executor: Executor, ttl: int = 60):
        self._executor = executor
        # Formato do cache: { cache_key: (timestamp, data) }
        self._cache = {}
        self.ttl = ttl  # Time-to-live em segundos

    def execute(self, command: Command):
        cache_key = command.get_cache_key()

        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            # Verifica se o cache não expirou (TTL)
            if (time.time() - timestamp) < self.ttl:
                print(f"CACHE HIT -> Retornando dados do cache para a chave: {cache_key}")
                # Apenas retorna o dado salvo, sem chamar o próximo executor
                print(f"  > Sucesso (do CACHE) ao processar Comando ID {getattr(command, 'id', 'N/A')}")
                return data
            else:
                print(f"CACHE STALE -> Dados expirados para a chave: {cache_key}")
                del self._cache[cache_key]

        print(f"CACHE MISS -> Executando e salvando no cache a chave: {cache_key}")
        # Se não está no cache ou expirou, executa a chamada real
        result = self._executor.execute(command)
        # Armazena o resultado no cache com o timestamp atual
        self._cache[cache_key] = (time.time(), result)
        return result


class CircuitBreakerDecorator(Executor):
    def __init__(self, executor: Executor, failure_threshold=3, recovery_timeout=10):
        self._executor = executor
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def execute(self, command: Command):
        if self.state == "OPEN":
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                print("CIRCUIT BREAKER -> Aberto, rejeitando a chamada.")
                raise ConnectionRefusedError("Circuit Breaker is open")

        try:
            result = self._executor.execute(command)
            self.failure_count = 0
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                print("CIRCUIT BREAKER -> Sucesso em HALF_OPEN. Fechando o circuito.")
            return result
        except Exception as e:
            self.failure_count += 1
            print(f"CIRCUIT BREAKER -> Falha detectada: {e}")
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = time.time()
                print("CIRCUIT BREAKER -> Limite de falhas atingido. Abrindo o circuito.")
            raise e

# --- Componente Principal ---
class Scheduler:
    def __init__(self, queue: RequestQueue, executor: Executor):
        self._queue = queue
        self._executor = executor
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def _run(self):
        print("Scheduler iniciado. Aguardando requisições...")
        while True:
            for command in self._queue:
                print("-" * 20)
                try:
                    self._executor.execute(command)
                    print(f"Scheduler: Comando executado com sucesso.")
                except Exception as e:
                    print(f"Scheduler: Falha ao executar comando: {e}")

                time.sleep(1)
            time.sleep(0.1)


# --- Implementação concreta do Command ---
class ProxyRequestCommand(Command):
    _id_counter = 0
    def __init__(self, payload: dict):
        self.payload = payload
        ProxyRequestCommand._id_counter += 1
        self.id = ProxyRequestCommand._id_counter

    def execute(self):
        response_data = {"status": "success", "processed_id": self.id, "payload": self.payload}
        print(f"  > Sucesso ao processar Comando ID {self.id} com payload: {self.payload}")
        return response_data

    def get_cache_key(self) -> str:
        """Cria uma chave estável a partir do payload para o cache."""
        return f"request:{json.dumps(self.payload, sort_keys=True)}"

    def __repr__(self):
        return f"ProxyRequestCommand(id={self.id}, payload={self.payload})"
