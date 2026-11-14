"""Afinação: frequência <-> número MIDI <-> nome da nota (temperamento igual, A4 = 440 Hz)."""
from __future__ import annotations

import math
import re

NOMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)$")


def midi_para_frequencia(midi: float, a4: float = 440.0) -> float:
    return a4 * 2 ** ((midi - 69) / 12)


def frequencia_para_midi(freq: float, a4: float = 440.0) -> float:
    """MIDI fracionário correspondente à frequência."""
    if freq <= 0:
        raise ValueError("frequência deve ser positiva")
    return 69 + 12 * math.log2(freq / a4)


def midi_para_nome(midi: int) -> str:
    """Ex.: 60 -> 'C4', 61 -> 'C#4' (C4 = dó central)."""
    if not 0 <= midi <= 127:
        raise ValueError("MIDI deve estar entre 0 e 127")
    return f"{NOMES[midi % 12]}{midi // 12 - 1}"


def nome_para_midi(nome: str) -> int:
    """Aceita sustenidos e bemóis ('C#4', 'Db4', 'a4')."""
    m = _RE.match(nome.strip())
    if not m:
        raise ValueError(f"nome de nota inválido: {nome!r}")
    letra, acidente, oitava = m.group(1).upper(), m.group(2), int(m.group(3))
    midi = _BASE[letra] + (1 if acidente == "#" else -1 if acidente == "b" else 0) + 12 * (oitava + 1)
    if not 0 <= midi <= 127:
        raise ValueError("nota fora da faixa MIDI")
    return midi


def nota_mais_proxima(freq: float, a4: float = 440.0) -> tuple[str, float]:
    """(nome da nota, desvio em cents) para a frequência."""
    m = frequencia_para_midi(freq, a4)
    n = round(m)
    return midi_para_nome(n), (m - n) * 100


def frequencia_do_nome(nome: str, a4: float = 440.0) -> float:
    return midi_para_frequencia(nome_para_midi(nome), a4)


def cents(f1: float, f2: float) -> float:
    """Intervalo de f1 para f2 em cents (1200 por oitava)."""
    if f1 <= 0 or f2 <= 0:
        raise ValueError("frequências devem ser positivas")
    return 1200 * math.log2(f2 / f1)
