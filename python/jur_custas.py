"""Custas judiciais por faixa de valor da causa (tabela de EXEMPLO, fictícia, injetável)."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

# (limite superior da faixa, percentual sobre o valor da causa); último limite None = sem teto de faixa
TABELA_EXEMPLO: list[tuple[Decimal | None, Decimal]] = [
    (Decimal("10000"), Decimal("1.0")),
    (Decimal("50000"), Decimal("1.5")),
    (Decimal("200000"), Decimal("2.0")),
    (None, Decimal("2.5")),
]
MINIMO_EXEMPLO = Decimal("50.00")
MAXIMO_EXEMPLO = Decimal("5000.00")
TAXA_RECURSO = Decimal("0.5")  # percentual adicional sobre as custas, no recurso


def _q(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def percentual_da_faixa(valor: Decimal, tabela=TABELA_EXEMPLO) -> Decimal:
    for limite, pct in tabela:
        if limite is None or valor <= limite:
            return pct
    raise ValueError("tabela sem faixa final aberta")


def calcular_custas(valor_causa: Decimal, minimo: Decimal = MINIMO_EXEMPLO, maximo: Decimal = MAXIMO_EXEMPLO,
                    tabela=TABELA_EXEMPLO) -> Decimal:
    """Aplica o percentual da faixa em que o valor cai (não escalonado), limitado a mínimo e máximo."""
    if valor_causa < 0:
        raise ValueError("valor da causa não pode ser negativo")
    if minimo > maximo:
        raise ValueError("mínimo maior que máximo")
    bruto = _q(valor_causa * percentual_da_faixa(valor_causa, tabela) / 100)
    return min(max(bruto, minimo), maximo)


def calcular_custas_progressivas(valor_causa: Decimal, minimo: Decimal = MINIMO_EXEMPLO,
                                 maximo: Decimal = MAXIMO_EXEMPLO, tabela=TABELA_EXEMPLO) -> Decimal:
    """Alíquotas marginais: cada faixa incide só sobre a parcela do valor que cabe nela."""
    if valor_causa < 0:
        raise ValueError("valor da causa não pode ser negativo")
    total, piso = Decimal("0"), Decimal("0")
    for limite, pct in tabela:
        topo = valor_causa if limite is None else min(valor_causa, limite)
        if topo > piso:
            total += (topo - piso) * pct / 100
        if limite is None or valor_causa <= limite:
            break
        piso = limite
    return min(max(_q(total), minimo), maximo)


def custas_recurso(valor_causa: Decimal) -> Decimal:
    """Preparo do recurso: custas da causa acrescidas da taxa adicional."""
    base = calcular_custas(valor_causa)
    return _q(base * (1 + TAXA_RECURSO))
