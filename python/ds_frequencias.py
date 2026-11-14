"""Tabela de frequências: absoluta, relativa, acumulada e percentual."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Hashable, Iterable


@dataclass(frozen=True)
class LinhaFrequencia:
    valor: Hashable
    absoluta: int
    relativa: float
    acumulada: int
    relativa_acumulada: float

    @property
    def percentual(self) -> float:
        return self.relativa * 100


def tabela_frequencias(dados: Iterable[Hashable], ordem: str = "valor") -> list[LinhaFrequencia]:
    """ordem: 'valor' (crescente), 'frequencia' (decrescente, desempate por valor)."""
    c = Counter(dados)
    total = sum(c.values())
    if total == 0:
        raise ValueError("dados vazios")
    if ordem == "valor":
        itens = sorted(c.items(), key=lambda kv: kv[0])
    elif ordem == "frequencia":
        itens = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    else:
        raise ValueError("ordem deve ser 'valor' ou 'frequencia'")
    linhas, acum = [], 0
    for valor, n in itens:
        acum += n
        linhas.append(LinhaFrequencia(valor, n, n / total, acum, acum / total))
    return linhas


def moda(dados: Iterable[Hashable]) -> list[Hashable]:
    c = Counter(dados)
    if not c:
        raise ValueError("dados vazios")
    m = max(c.values())
    return sorted(v for v, n in c.items() if n == m)


def formatar(linhas: list[LinhaFrequencia]) -> str:
    saida = [f"{'valor':<10}{'abs':>5}{'%':>8}{'acum':>6}"]
    for l in linhas:
        saida.append(f"{str(l.valor):<10}{l.absoluta:>5}{l.percentual:>8.1f}{l.acumulada:>6}")
    return "\n".join(saida)
