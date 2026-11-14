"""Marcação a mercado de título de renda fixa: preço, YTM e duration."""
from __future__ import annotations


def _fluxos(face: float, taxa_cupom: float, periodos: int) -> list[float]:
    if face <= 0 or periodos <= 0 or taxa_cupom < 0:
        raise ValueError("face e períodos devem ser positivos; cupom >= 0")
    cupom = face * taxa_cupom
    return [cupom] * (periodos - 1) + [cupom + face]


def preco_titulo(face: float, taxa_cupom: float, ytm: float, periodos: int) -> float:
    """Preço = soma dos fluxos descontados à taxa `ytm` por período."""
    if ytm <= -1:
        raise ValueError("ytm deve ser maior que -100%")
    return sum(
        f / (1 + ytm) ** t for t, f in enumerate(_fluxos(face, taxa_cupom, periodos), 1)
    )


def duration_macaulay(face: float, taxa_cupom: float, ytm: float, periodos: int) -> float:
    fluxos = _fluxos(face, taxa_cupom, periodos)
    pv = [f / (1 + ytm) ** t for t, f in enumerate(fluxos, 1)]
    return sum(t * v for t, v in enumerate(pv, 1)) / sum(pv)


def duration_modificada(face: float, taxa_cupom: float, ytm: float, periodos: int) -> float:
    return duration_macaulay(face, taxa_cupom, ytm, periodos) / (1 + ytm)


def ytm_por_preco(
    preco: float, face: float, taxa_cupom: float, periodos: int, tol: float = 1e-12
) -> float:
    """Taxa que iguala o valor presente ao preço (bisseção; preço decresce com a taxa)."""
    if preco <= 0:
        raise ValueError("preço deve ser positivo")
    baixo, alto = -0.99, 1.0
    while preco_titulo(face, taxa_cupom, alto, periodos) > preco:
        alto *= 2
        if alto > 1e6:
            raise ValueError("preço inalcançável")
    if preco_titulo(face, taxa_cupom, baixo, periodos) < preco:
        raise ValueError("preço inalcançável")
    while alto - baixo > tol:
        meio = (baixo + alto) / 2
        if preco_titulo(face, taxa_cupom, meio, periodos) > preco:
            baixo = meio
        else:
            alto = meio
    return (baixo + alto) / 2
