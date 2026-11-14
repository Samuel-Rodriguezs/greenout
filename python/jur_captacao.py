"""Contratos de captação e comissão por parceiro (parâmetros de exemplo, injetáveis)."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


def _q(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ContratoCaptacao:
    parceiro: str
    percentual: Decimal  # % sobre honorários recebidos
    fixo_por_caso: Decimal = Decimal("0")
    teto_por_caso: Decimal | None = None
    # faixas de bônus por volume mensal: (casos mínimos, bônus em pontos percentuais)
    bonus_volume: tuple[tuple[int, Decimal], ...] = ()

    def __post_init__(self) -> None:
        if not Decimal("0") <= self.percentual <= 100:
            raise ValueError("percentual deve estar entre 0 e 100")
        if self.fixo_por_caso < 0 or (self.teto_por_caso is not None and self.teto_por_caso < 0):
            raise ValueError("valores não podem ser negativos")


def percentual_efetivo(c: ContratoCaptacao, casos_no_mes: int) -> Decimal:
    """Percentual base mais o maior bônus de volume atingido."""
    bonus = max((b for minimo, b in c.bonus_volume if casos_no_mes >= minimo), default=Decimal("0"))
    return c.percentual + bonus


def comissao_do_caso(c: ContratoCaptacao, honorarios_recebidos: Decimal, casos_no_mes: int = 1) -> Decimal:
    if honorarios_recebidos < 0:
        raise ValueError("honorários não podem ser negativos")
    valor = _q(honorarios_recebidos * percentual_efetivo(c, casos_no_mes) / 100) + c.fixo_por_caso
    if c.teto_por_caso is not None:
        valor = min(valor, c.teto_por_caso)
    return _q(valor)


@dataclass(frozen=True)
class CasoCaptado:
    parceiro: str
    mes: str  # "AAAA-MM"
    honorarios_recebidos: Decimal


def comissoes_do_mes(contratos: dict[str, ContratoCaptacao], casos: list[CasoCaptado], mes: str) -> dict[str, Decimal]:
    """Total de comissão por parceiro no mês; o volume do mês define o bônus de todos os seus casos."""
    do_mes = [c for c in casos if c.mes == mes]
    volume: dict[str, int] = {}
    for c in do_mes:
        volume[c.parceiro] = volume.get(c.parceiro, 0) + 1
    total: dict[str, Decimal] = {}
    for c in do_mes:
        if c.parceiro not in contratos:
            raise KeyError(f"parceiro sem contrato: {c.parceiro}")
        v = comissao_do_caso(contratos[c.parceiro], c.honorarios_recebidos, volume[c.parceiro])
        total[c.parceiro] = total.get(c.parceiro, Decimal("0")) + v
    return dict(sorted(total.items()))
