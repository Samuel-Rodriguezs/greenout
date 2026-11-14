"""Mesclagem de intervalos de calendário e busca de horários livres."""

from __future__ import annotations

Intervalo = tuple[int, int]


def mesclar(intervalos: list[Intervalo]) -> list[Intervalo]:
    """Une intervalos sobrepostos ou adjacentes (fim == início)."""
    for ini, fim in intervalos:
        if ini > fim:
            raise ValueError(f"intervalo invertido: ({ini}, {fim})")
    res: list[Intervalo] = []
    for ini, fim in sorted(intervalos):
        if res and ini <= res[-1][1]:
            res[-1] = (res[-1][0], max(res[-1][1], fim))
        else:
            res.append((ini, fim))
    return res


def horarios_livres(ocupados: list[Intervalo], inicio_dia: int, fim_dia: int) -> list[Intervalo]:
    """Lacunas dentro de [inicio_dia, fim_dia] não cobertas por compromissos."""
    if inicio_dia > fim_dia:
        raise ValueError("expediente inválido")
    livres: list[Intervalo] = []
    cursor = inicio_dia
    for ini, fim in mesclar(ocupados):
        if fim <= cursor:
            continue
        if ini > fim_dia:
            break
        if ini > cursor:
            livres.append((cursor, ini))
        cursor = max(cursor, fim)
    if cursor < fim_dia:
        livres.append((cursor, fim_dia))
    return livres


def tem_conflito(intervalos: list[Intervalo]) -> bool:
    """True se dois compromissos se sobrepõem (encostar nas pontas não conta)."""
    ordenados = sorted(intervalos)
    return any(b[0] < a[1] for a, b in zip(ordenados, ordenados[1:]))


def inserir(intervalos: list[Intervalo], novo: Intervalo) -> list[Intervalo]:
    """Insere um intervalo numa lista já mesclada e mantém a lista mesclada."""
    return mesclar(intervalos + [novo])
