"""Relatório de produtividade por advogado (peças, audiências, horas e taxa de cumprimento de prazos)."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Atividade:
    advogado: str
    data: date
    tipo: str  # "peca", "audiencia", "reuniao" ...
    horas: float
    prazo_cumprido: bool | None = None  # None quando a atividade não tem prazo


@dataclass(frozen=True)
class Resumo:
    advogado: str
    atividades: int
    horas: float
    por_tipo: dict[str, int]
    taxa_prazos: float | None  # 0..100, None se não houve prazos

    @property
    def horas_por_atividade(self) -> float:
        return round(self.horas / self.atividades, 2) if self.atividades else 0.0


def relatorio(atividades: list[Atividade], inicio: date, fim: date) -> list[Resumo]:
    """Resumo por advogado no período [inicio, fim], ordenado por horas (maior primeiro) e nome."""
    if fim < inicio:
        raise ValueError("período inválido")
    grupos: dict[str, list[Atividade]] = defaultdict(list)
    for a in atividades:
        if a.horas < 0:
            raise ValueError("horas não podem ser negativas")
        if inicio <= a.data <= fim:
            grupos[a.advogado].append(a)
    resumos = []
    for adv, itens in grupos.items():
        tipos: dict[str, int] = defaultdict(int)
        for i in itens:
            tipos[i.tipo] += 1
        com_prazo = [i for i in itens if i.prazo_cumprido is not None]
        taxa = round(100 * sum(1 for i in com_prazo if i.prazo_cumprido) / len(com_prazo), 1) if com_prazo else None
        resumos.append(Resumo(adv, len(itens), round(sum(i.horas for i in itens), 2), dict(sorted(tipos.items())), taxa))
    return sorted(resumos, key=lambda r: (-r.horas, r.advogado))


def destaque(resumos: list[Resumo]) -> str | None:
    """Advogado com mais atividades (desempate: mais horas, depois nome)."""
    if not resumos:
        return None
    return min(resumos, key=lambda r: (-r.atividades, -r.horas, r.advogado)).advogado


def total_horas(resumos: list[Resumo]) -> float:
    return round(sum(r.horas for r in resumos), 2)
