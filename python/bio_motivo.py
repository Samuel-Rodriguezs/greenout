"""Busca de motivos com até k incompatibilidades (mismatches)."""


def buscar(seq: str, motivo: str, max_mismatches: int = 0) -> list[tuple[int, int]]:
    """Lista de (posição base 0, nº de mismatches) para cada ocorrência."""
    if not motivo:
        raise ValueError("motivo vazio")
    if max_mismatches < 0:
        raise ValueError("max_mismatches negativo")
    m = len(motivo)
    achados = []
    for i in range(len(seq) - m + 1):
        d = 0
        for x, y in zip(seq[i : i + m], motivo):
            if x != y:
                d += 1
                if d > max_mismatches:
                    break
        else:
            achados.append((i, d))
    return achados


def contar(seq: str, motivo: str, max_mismatches: int = 0) -> int:
    return len(buscar(seq, motivo, max_mismatches))


def buscar_ambas_fitas(
    seq: str, motivo: str, max_mismatches: int = 0
) -> list[tuple[int, str, int]]:
    """Ocorrências do motivo na fita direta ('+') e do seu complemento reverso ('-')."""
    rc = motivo.translate(str.maketrans("ACGT", "TGCA"))[::-1]
    res = [(p, "+", d) for p, d in buscar(seq, motivo, max_mismatches)]
    if rc != motivo:
        res += [(p, "-", d) for p, d in buscar(seq, rc, max_mismatches)]
    return sorted(res)
