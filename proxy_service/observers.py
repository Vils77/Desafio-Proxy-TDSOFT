# proxy_service/observers.py

from patterns import Observer

class StructuredLogger(Observer):
    """Observer que registra logs estruturados dos eventos."""
    def update(self, subject, event, *args, **kwargs):
        command = kwargs.get('command')
        if event == "enqueued":
            print(f"LOG | Evento: {event} | Comando: {command} | Tamanho Fila: {kwargs.get('queue_size')}")
        elif event == "dropped":
            print(f"LOG | Evento: {event} | Motivo: {kwargs.get('reason')} | Comando: {command}")
        else:
            print(f"LOG | Evento: {event} | Fonte: {type(subject).__name__}")


class MetricsCollector(Observer):
    """
    Observer que coleta métricas. Em uma aplicação real, isso seria
    integrado a um sistema como Prometheus.
    """
    def __init__(self):
        self.enqueued_count = 0
        self.dropped_count = 0

    def update(self, subject, event, *args, **kwargs):
        if event == "enqueued":
            self.enqueued_count += 1
        elif event == "dropped":
            self.dropped_count += 1

    def print_metrics(self):
        print("\n--- MÉTRICAS ---")
        print(f"Total de Requisições Enfileiradas: {self.enqueued_count}")
        print(f"Total de Requisições Descartadas: {self.dropped_count}")
        print("----------------\n")
