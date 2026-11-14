"""Merge de intervalos sobrepostos."""


def mesclar_intervalos(intervalos: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Une intervalos que se sobrepõem ou se tocam; retorna ordenado."""
    for ini, fim in intervalos:
        if ini > fim:
            raise ValueError(f"intervalo inválido: ({ini}, {fim})")
    resultado: list[tuple[int, int]] = []
    for ini, fim in sorted(intervalos):
        if resultado and ini <= resultado[-1][1]:
            resultado[-1] = (resultado[-1][0], max(resultado[-1][1], fim))
        else:
            resultado.append((ini, fim))
    return resultado
