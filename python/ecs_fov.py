"""Campo de visão (FOV) por recursive shadowcasting em 8 octantes."""
from __future__ import annotations

from typing import Callable

_MULT = (
    (1, 0, 0, -1, -1, 0, 0, 1),
    (0, 1, -1, 0, 0, -1, 1, 0),
    (0, 1, 1, 0, 0, -1, -1, 0),
    (1, 0, 0, 1, -1, 0, 0, -1),
)


def campo_visao(
    origem: tuple[int, int],
    raio: int,
    bloqueia: Callable[[int, int], bool],
) -> set[tuple[int, int]]:
    """Células visíveis a partir de `origem` em até `raio` (distância euclidiana).

    Células opacas (paredes) vistas de frente fazem parte do resultado; o que
    está atrás delas, não. `bloqueia(x, y)` deve aceitar coordenadas fora do mapa.
    """
    if raio < 0:
        raise ValueError("raio não pode ser negativo")
    ox, oy = origem
    visiveis = {origem}
    for octante in range(8):
        _varrer(ox, oy, 1, 1.0, 0.0, raio, _MULT[0][octante], _MULT[1][octante],
                _MULT[2][octante], _MULT[3][octante], bloqueia, visiveis)
    return visiveis


def _varrer(cx, cy, linha, inicio, fim, raio, xx, xy, yx, yy, bloqueia, visiveis) -> None:
    if inicio < fim:
        return
    r2 = raio * raio
    novo_inicio = 0.0
    for j in range(linha, raio + 1):
        dx, dy = -j - 1, -j
        bloqueado = False
        while dx <= 0:
            dx += 1
            x, y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
            esq = (dx - 0.5) / (dy + 0.5)
            dir_ = (dx + 0.5) / (dy - 0.5)
            if inicio < dir_:
                continue
            if fim > esq:
                break
            if dx * dx + dy * dy <= r2:
                visiveis.add((x, y))
            if bloqueado:
                if bloqueia(x, y):
                    novo_inicio = dir_
                else:
                    bloqueado = False
                    inicio = novo_inicio
            elif bloqueia(x, y) and j < raio:
                bloqueado = True
                _varrer(cx, cy, j + 1, inicio, esq, raio, xx, xy, yx, yy, bloqueia, visiveis)
                novo_inicio = dir_
        if bloqueado:
            break
