"""Temperatura de fusão (Tm) de oligonucleotídeos."""


def _contar(seq: str) -> tuple[int, int, int]:
    seq = seq.upper()
    if not seq or set(seq) - set("ACGT"):
        raise ValueError("oligo inválido")
    gc = seq.count("G") + seq.count("C")
    return gc, len(seq) - gc, len(seq)


def tm_wallace(seq: str) -> float:
    """Regra de Wallace: 2*(A+T) + 4*(G+C); apropriada para oligos curtos."""
    gc, at, _ = _contar(seq)
    return float(2 * at + 4 * gc)


def tm_gc(seq: str) -> float:
    """Fórmula baseada em GC: 64,9 + 41*(GC - 16,4)/N."""
    gc, _, n = _contar(seq)
    return 64.9 + 41 * (gc - 16.4) / n


def tm(seq: str) -> float:
    """Wallace para menos de 14 nt; fórmula de GC para os demais."""
    return tm_wallace(seq) if len(seq) < 14 else tm_gc(seq)
