"""Resumo da carteira de processos: quantidade e valor da causa por área."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from jur_processos import Fase, Processo


@dataclass(frozen=True)
class LinhaArea:
    area: str
    quantidade: int
    total: Decimal
    media: Decimal
    maior: Decimal
    participacao: Decimal  # % do valor total da carteira


def resumo_por_area(processos: list[Processo], incluir_encerrados: bool = False) -> list[LinhaArea]:
    """Linhas por área, ordenadas por valor total decrescente (desempate por nome)."""
    ativos = [p for p in processos if incluir_encerrados or p.fase != Fase.ENCERRADO]
    grupos: dict[str, list[Decimal]] = defaultdict(list)
    for p in ativos:
        grupos[p.area].append(p.valor_causa)
    geral = sum((sum(v, Decimal("0")) for v in grupos.values()), Decimal("0"))
    linhas = []
    for area, valores in grupos.items():
        total = sum(valores, Decimal("0"))
        part = (total * 100 / geral).quantize(Decimal("0.01")) if geral else Decimal("0.00")
        linhas.append(LinhaArea(area, len(valores), total, (total / len(valores)).quantize(Decimal("0.01")),
                                max(valores), part))
    return sorted(linhas, key=lambda l: (-l.total, l.area))


def total_carteira(processos: list[Processo], incluir_encerrados: bool = False) -> Decimal:
    return sum((l.total for l in resumo_por_area(processos, incluir_encerrados)), Decimal("0"))


def por_advogado(processos: list[Processo]) -> dict[str, tuple[int, Decimal]]:
    """Advogado -> (quantidade, valor total) dos processos não encerrados."""
    res: dict[str, tuple[int, Decimal]] = {}
    for p in processos:
        if p.fase == Fase.ENCERRADO:
            continue
        q, t = res.get(p.advogado, (0, Decimal("0")))
        res[p.advogado] = (q + 1, t + p.valor_causa)
    return dict(sorted(res.items()))


def concentracao(processos: list[Processo], n: int = 3) -> Decimal:
    """Percentual do valor da carteira concentrado nos n maiores processos ativos."""
    valores = sorted((p.valor_causa for p in processos if p.fase != Fase.ENCERRADO), reverse=True)
    total = sum(valores, Decimal("0"))
    if not total:
        return Decimal("0.00")
    return (sum(valores[:n], Decimal("0")) * 100 / total).quantize(Decimal("0.01"))
