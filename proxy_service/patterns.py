# proxy_service/patterns.py

from abc import ABC, abstractmethod
from typing import List, Any

# --- Padrão Observer ---

class Observer(ABC):
    """Interface para os Observers que reagem a eventos."""
    @abstractmethod
    def update(self, subject: Any, event: str, *args, **kwargs):
        pass

class Subject:
    """Classe base para os Subjects que emitem eventos."""
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, event: str, *args, **kwargs):
        """Notifica todos os observers sobre um evento."""
        for observer in self._observers:
            observer.update(self, event, *args, **kwargs)

# --- Padrão Command ---

class Command(ABC):
    """Interface para encapsular uma requisição como um objeto."""
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def get_cache_key(self) -> str:
        """Retorna uma chave única e estável para fins de cache."""
        pass
