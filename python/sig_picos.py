"""Detecção de picos em sinais discretos."""
from __future__ import annotations


def picos(x: list[float], altura_min: float | None = None, distancia_min: int = 1,
          proeminencia_min: float = 0.0) -> list[int]:
    """Índices de máximos locais estritos (platôs usam o índice central).

    Filtra por altura, proeminência e distância mínima (prefere picos mais altos).
    """
    if distancia_min < 1:
        raise ValueError("distancia_min deve ser >= 1")
    candidatos: list[int] = []
    i = 1
    n = len(x)
    while i < n - 1:
        if x[i - 1] < x[i]:
            j = i
            while j + 1 < n and x[j + 1] == x[i]:
                j += 1
            if j + 1 < n and x[j + 1] < x[i]:
                candidatos.append((i + j) // 2)
            i = j + 1
        else:
            i += 1
    if altura_min is not None:
        candidatos = [p for p in candidatos if x[p] >= altura_min]
    if proeminencia_min > 0:
        candidatos = [p for p in candidatos if proeminencia(x, p) >= proeminencia_min]
    if distancia_min > 1:
        candidatos = _filtrar_distancia(x, candidatos, distancia_min)
    return candidatos


def proeminencia(x: list[float], p: int) -> float:
    """Altura do pico acima da maior das duas bases (mínimos até um pico mais alto)."""
    def base(direcao: int) -> float:
        minimo = x[p]
        i = p + direcao
        while 0 <= i < len(x) and x[i] <= x[p]:
            minimo = min(minimo, x[i])
            i += direcao
        return minimo

    return x[p] - max(base(-1), base(1))


def _filtrar_distancia(x: list[float], cands: list[int], d: int) -> list[int]:
    mantidos: list[int] = []
    for p in sorted(cands, key=lambda i: -x[i]):
        if all(abs(p - q) >= d for q in mantidos):
            mantidos.append(p)
    return sorted(mantidos)


def vales(x: list[float], **kw) -> list[int]:
    """Mínimos locais (picos do sinal invertido); `altura_min` vale para o sinal invertido."""
    return picos([-v for v in x], **kw)
