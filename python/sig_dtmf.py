"""DTMF: geração de tons e detecção com o algoritmo de Goertzel."""
from __future__ import annotations

import math

LINHAS = (697.0, 770.0, 852.0, 941.0)
COLUNAS = (1209.0, 1336.0, 1477.0, 1633.0)
TECLAS = ("123A", "456B", "789C", "*0#D")


def frequencias_da_tecla(tecla: str) -> tuple[float, float]:
    """(frequência da linha, frequência da coluna)."""
    for i, linha in enumerate(TECLAS):
        j = linha.find(tecla) if len(tecla) == 1 else -1
        if j >= 0:
            return LINHAS[i], COLUNAS[j]
    raise ValueError(f"tecla inválida: {tecla!r}")


def gerar_tecla(tecla: str, taxa: float, duracao: float, amp: float = 0.5) -> list[float]:
    """Soma de dois senos."""
    fl, fc = frequencias_da_tecla(tecla)
    n = round(duracao * taxa)
    return [
        amp * (math.sin(2 * math.pi * fl * i / taxa) + math.sin(2 * math.pi * fc * i / taxa)) / 2
        for i in range(n)
    ]


def gerar_sequencia(teclas: str, taxa: float, duracao: float = 0.1, pausa: float = 0.05) -> list[float]:
    """Tons separados por silêncio."""
    saida: list[float] = []
    silencio = [0.0] * round(pausa * taxa)
    for t in teclas:
        saida += gerar_tecla(t, taxa, duracao) + silencio
    return saida


def goertzel(x: list[float], freq: float, taxa: float) -> float:
    """Potência da componente em `freq` (quadrado da magnitude da DFT, sem normalização)."""
    if taxa <= 0:
        raise ValueError("taxa deve ser positiva")
    w = 2 * math.pi * freq / taxa
    coef = 2 * math.cos(w)
    s1 = s2 = 0.0
    for v in x:
        s1, s2 = v + coef * s1 - s2, s1
    return s1 * s1 + s2 * s2 - coef * s1 * s2


def detectar_tecla(x: list[float], taxa: float, limiar: float = 0.1) -> str | None:
    """Detecta uma tecla num trecho; None se não houver par de tons válido.

    `limiar` é a fração mínima da energia total que o par de tons deve conter.
    """
    if not x:
        return None
    energia = sum(v * v for v in x)
    if energia == 0:
        return None
    pl = [goertzel(x, f, taxa) for f in LINHAS]
    pc = [goertzel(x, f, taxa) for f in COLUNAS]
    i = max(range(4), key=lambda k: pl[k])
    j = max(range(4), key=lambda k: pc[k])
    # Goertzel de um seno de amplitude a vale (N a/2)^2 e sua energia N a^2/2: fração = 2P/N/E
    n = len(x)
    if (pl[i] + pc[j]) * 2 / n / energia < limiar:
        return None
    # cada tom deve dominar os vizinhos da mesma faixa
    for p, k in ((pl, i), (pc, j)):
        outros = [p[m] for m in range(4) if m != k]
        if p[k] < 4 * max(outros):
            return None
    return TECLAS[i][j]


def decodificar_sequencia(x: list[float], taxa: float, duracao: float = 0.1, pausa: float = 0.05) -> str:
    """Inverso de gerar_sequencia: fatia em blocos de tom+pausa e detecta cada um."""
    tom = round(duracao * taxa)
    passo = tom + round(pausa * taxa)
    saida = []
    for ini in range(0, len(x), passo):
        t = detectar_tecla(x[ini: ini + tom], taxa)
        if t is not None:
            saida.append(t)
    return "".join(saida)
