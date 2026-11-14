"""Observer: ação na bolsa notifica assinantes quando o preço varia."""
from __future__ import annotations

from typing import Callable

Assinante = Callable[[str, float, float], None]


class Acao:
    def __init__(self, simbolo: str, preco: float) -> None:
        self.simbolo = simbolo
        self._preco = preco
        self._assinantes: list[Assinante] = []

    def assinar(self, fn: Assinante) -> Callable[[], None]:
        self._assinantes.append(fn)

        def cancelar() -> None:
            if fn in self._assinantes:
                self._assinantes.remove(fn)

        return cancelar

    @property
    def preco(self) -> float:
        return self._preco

    @preco.setter
    def preco(self, novo: float) -> None:
        antigo, self._preco = self._preco, novo
        if novo != antigo:
            for fn in list(self._assinantes):
                fn(self.simbolo, antigo, novo)


class AlertaQueda:
    def __init__(self, limite_pct: float) -> None:
        self.limite_pct = limite_pct
        self.alertas: list[str] = []

    def __call__(self, simbolo: str, antigo: float, novo: float) -> None:
        queda = (antigo - novo) / antigo * 100
        if queda >= self.limite_pct:
            self.alertas.append(f"{simbolo} caiu {queda:.1f}%")
