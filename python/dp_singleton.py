"""Singleton: registro de configuração global da aplicação."""
from __future__ import annotations

import threading
from typing import Any, Optional


class Configuracao:
    _instancia: Optional["Configuracao"] = None
    _trava = threading.Lock()

    def __new__(cls) -> "Configuracao":
        if cls._instancia is None:
            with cls._trava:
                if cls._instancia is None:
                    inst = super().__new__(cls)
                    inst._valores = {}
                    cls._instancia = inst
        return cls._instancia

    def definir(self, chave: str, valor: Any) -> None:
        self._valores[chave] = valor

    def obter(self, chave: str, padrao: Any = None) -> Any:
        return self._valores.get(chave, padrao)

    @classmethod
    def resetar(cls) -> None:
        cls._instancia = None
