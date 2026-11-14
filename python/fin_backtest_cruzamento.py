"""Backtest de cruzamento de médias móveis (long-only) com custo por operação."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoBacktest:
    patrimonio: list[float]  # começa em 1.0
    posicoes: list[int]  # 1 = comprado, 0 = fora, em cada instante
    n_operacoes: int
    retorno_total: float


def _sma(precos: list[float], n: int) -> list[float | None]:
    saida: list[float | None] = [None] * len(precos)
    for i in range(n - 1, len(precos)):
        saida[i] = sum(precos[i - n + 1 : i + 1]) / n
    return saida


def backtest_cruzamento(
    precos: list[float], curta: int, longa: int, custo: float = 0.0
) -> ResultadoBacktest:
    """Compra quando SMA curta > SMA longa no fechamento de t-1; a posição vale
    para o retorno de t (sem look-ahead). `custo` é a fração do patrimônio paga a
    cada entrada ou saída."""
    if not 0 < curta < longa:
        raise ValueError("é necessário 0 < curta < longa")
    if custo < 0 or custo >= 1:
        raise ValueError("custo deve estar em [0, 1)")
    if any(p <= 0 for p in precos):
        raise ValueError("preços devem ser positivos")
    mc, ml = _sma(precos, curta), _sma(precos, longa)
    sinal = [
        1 if c is not None and lg is not None and c > lg else 0
        for c, lg in zip(mc, ml)
    ]
    posicoes = [0] + sinal[:-1] if precos else []
    patrimonio = [1.0] if precos else []
    operacoes = 0
    for t in range(1, len(precos)):
        valor = patrimonio[-1]
        if posicoes[t] != posicoes[t - 1]:
            valor *= 1 - custo
            operacoes += 1
        if posicoes[t]:
            valor *= precos[t] / precos[t - 1]
        patrimonio.append(valor)
    total = patrimonio[-1] - 1 if patrimonio else 0.0
    return ResultadoBacktest(patrimonio, posicoes, operacoes, total)
