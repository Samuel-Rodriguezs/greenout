"""Signo do zodíaco (tropical) a partir de uma data."""
from __future__ import annotations

from datetime import date

# (mês, dia inicial, nome); cada signo vai até a véspera do início do próximo.
_INICIOS: tuple[tuple[int, int, str], ...] = (
    (1, 20, "Aquário"),
    (2, 19, "Peixes"),
    (3, 21, "Áries"),
    (4, 20, "Touro"),
    (5, 21, "Gêmeos"),
    (6, 21, "Câncer"),
    (7, 23, "Leão"),
    (8, 23, "Virgem"),
    (9, 23, "Libra"),
    (10, 23, "Escorpião"),
    (11, 22, "Sagitário"),
    (12, 22, "Capricórnio"),
)

ELEMENTOS = {
    "Áries": "Fogo", "Leão": "Fogo", "Sagitário": "Fogo",
    "Touro": "Terra", "Virgem": "Terra", "Capricórnio": "Terra",
    "Gêmeos": "Ar", "Libra": "Ar", "Aquário": "Ar",
    "Câncer": "Água", "Escorpião": "Água", "Peixes": "Água",
}


def signo(d: date | None = None, *, mes: int | None = None, dia: int | None = None) -> str:
    """Signo de uma data (ou de mês/dia; 29/02 é aceito)."""
    if d is not None:
        mes, dia = d.month, d.day
    if mes is None or dia is None:
        raise ValueError("informe uma data ou mes e dia")
    # valida usando um ano bissexto
    date(2000, mes, dia)
    resultado = "Capricórnio"  # até 19/01
    for m, di, nome in _INICIOS:
        if (mes, dia) >= (m, di):
            resultado = nome
    return resultado


def elemento(nome_signo: str) -> str:
    return ELEMENTOS[nome_signo]
