"""Taxa Interna de Retorno (TIR) por bisseção."""
from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from dom_vpl import vpl_exato


def tir(fluxos: Sequence[object], baixo: str = "-0.99", alto: str = "10",
        tolerancia: str = "1e-10", max_iter: int = 500) -> Decimal:
    """Raiz de VPL(i) = 0 no intervalo [baixo, alto].

    Exige mudança de sinal do VPL nas pontas; do contrário levanta ValueError
    (fluxos sem troca de sinal não têm TIR).
    """
    fl = [Decimal(str(f)) for f in fluxos]
    if len(fl) < 2:
        raise ValueError("são necessários ao menos dois fluxos")
    if not (any(f < 0 for f in fl) and any(f > 0 for f in fl)):
        raise ValueError("fluxos precisam ter sinais diferentes")
    lo, hi = Decimal(baixo), Decimal(alto)
    f_lo, f_hi = vpl_exato(lo, fl), vpl_exato(hi, fl)
    if f_lo == 0:
        return lo
    if f_hi == 0:
        return hi
    if (f_lo > 0) == (f_hi > 0):
        raise ValueError("não há raiz no intervalo informado")
    tol = Decimal(tolerancia)
    for _ in range(max_iter):
        meio = (lo + hi) / 2
        f_meio = vpl_exato(meio, fl)
        if f_meio == 0 or (hi - lo) / 2 < tol:
            return meio
        if (f_meio > 0) == (f_lo > 0):
            lo, f_lo = meio, f_meio
        else:
            hi = meio
    return (lo + hi) / 2
