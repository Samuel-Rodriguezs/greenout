"""Paginação por offset (página/tamanho) e por cursor opaco (keyset)."""
from __future__ import annotations

import base64
import json
import math
from dataclasses import dataclass
from typing import Any, Callable, Sequence


@dataclass
class Pagina:
    itens: list[Any]
    pagina: int
    por_pagina: int
    total: int

    @property
    def paginas(self) -> int:
        return max(1, math.ceil(self.total / self.por_pagina))

    @property
    def tem_proxima(self) -> bool:
        return self.pagina < self.paginas

    @property
    def tem_anterior(self) -> bool:
        return self.pagina > 1

    def meta(self) -> dict[str, int | bool]:
        return {"pagina": self.pagina, "por_pagina": self.por_pagina, "total": self.total,
                "paginas": self.paginas, "tem_proxima": self.tem_proxima,
                "tem_anterior": self.tem_anterior}


def paginar(itens: Sequence[Any], pagina: int = 1, por_pagina: int = 20,
            maximo: int = 100) -> Pagina:
    if pagina < 1:
        raise ValueError("pagina deve ser >= 1")
    if not 1 <= por_pagina <= maximo:
        raise ValueError(f"por_pagina deve estar entre 1 e {maximo}")
    ini = (pagina - 1) * por_pagina
    return Pagina(list(itens[ini:ini + por_pagina]), pagina, por_pagina, len(itens))


def parse_parametros(query: dict[str, list[str]], por_pagina_padrao: int = 20,
                     maximo: int = 100) -> tuple[int, int]:
    """Lê ?pagina=&por_pagina= de uma query já parseada, com limites."""
    def inteiro(nome: str, padrao: int) -> int:
        v = query.get(nome, [None])[0]
        if v is None:
            return padrao
        try:
            return int(v)
        except ValueError:
            raise ValueError(f"{nome} deve ser inteiro") from None
    return inteiro("pagina", 1), min(inteiro("por_pagina", por_pagina_padrao), maximo)


def codificar_cursor(valor: Any) -> str:
    bruto = json.dumps(valor, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(bruto).decode().rstrip("=")


def decodificar_cursor(cursor: str) -> Any:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
    except (ValueError, UnicodeDecodeError):
        raise ValueError("cursor inválido") from None


def paginar_cursor(itens: Sequence[Any], chave: Callable[[Any], Any], limite: int = 20,
                   cursor: str | None = None) -> tuple[list[Any], str | None]:
    """Devolve (itens, proximo_cursor); os itens precisam estar ordenados por `chave` crescente.

    O cursor codifica a chave do último item entregue, então inserções/remoções
    anteriores não deslocam a janela (ao contrário de offset).
    """
    if limite < 1:
        raise ValueError("limite deve ser >= 1")
    inicio = 0
    if cursor is not None:
        ultima = decodificar_cursor(cursor)
        inicio = len(itens)
        for i, it in enumerate(itens):
            if chave(it) > ultima:
                inicio = i
                break
    janela = list(itens[inicio:inicio + limite])
    proximo = None
    if inicio + limite < len(itens) and janela:
        proximo = codificar_cursor(chave(janela[-1]))
    return janela, proximo
