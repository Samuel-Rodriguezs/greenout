"""Barramento de eventos publish/subscribe com wildcard '*' no fim do topico."""
from typing import Any, Callable, Dict, List, Tuple

Handler = Callable[[str, Any], None]


class BarramentoEventos:
    def __init__(self) -> None:
        self._assinaturas: List[Tuple[int, str, Handler]] = []
        self._proximo_id = 1
        self.erros: List[Tuple[str, Exception]] = []

    def assinar(self, padrao: str, handler: Handler) -> int:
        if not padrao:
            raise ValueError("topico vazio")
        if not callable(handler):
            raise TypeError("handler deve ser chamavel")
        id_ = self._proximo_id
        self._proximo_id += 1
        self._assinaturas.append((id_, padrao, handler))
        return id_

    def cancelar(self, id_: int) -> None:
        antes = len(self._assinaturas)
        self._assinaturas = [a for a in self._assinaturas if a[0] != id_]
        if len(self._assinaturas) == antes:
            raise KeyError(f"assinatura {id_} inexistente")

    @staticmethod
    def _casa(padrao: str, topico: str) -> bool:
        if padrao.endswith("*"):
            return topico.startswith(padrao[:-1])
        return padrao == topico

    def publicar(self, topico: str, dados: Any = None) -> int:
        """Entrega aos assinantes; erro de um handler nao impede os demais."""
        entregas = 0
        for _, padrao, handler in list(self._assinaturas):
            if self._casa(padrao, topico):
                try:
                    handler(topico, dados)
                    entregas += 1
                except Exception as e:  # noqa: BLE001
                    self.erros.append((topico, e))
        return entregas
