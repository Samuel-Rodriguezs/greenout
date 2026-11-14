"""Massa monoisotópica de peptídeos."""

AGUA = 18.010565

MASSAS: dict[str, float] = {
    "G": 57.02146, "A": 71.03711, "S": 87.03203, "P": 97.05276,
    "V": 99.06841, "T": 101.04768, "C": 103.00919, "L": 113.08406,
    "I": 113.08406, "N": 114.04293, "D": 115.02694, "Q": 128.05858,
    "K": 128.09496, "E": 129.04259, "M": 131.04049, "H": 137.05891,
    "F": 147.06841, "R": 156.10111, "Y": 163.06333, "W": 186.07931,
}


def massa(peptideo: str) -> float:
    """Massa monoisotópica neutra: soma dos resíduos + uma água."""
    if not peptideo:
        raise ValueError("peptídeo vazio")
    try:
        return sum(MASSAS[a] for a in peptideo.upper()) + AGUA
    except KeyError as e:
        raise ValueError(f"aminoácido inválido: {e.args[0]!r}") from None


def mz(peptideo: str, carga: int = 1) -> float:
    """Razão m/z do íon [M + zH]^z+ (próton = 1,007276)."""
    if carga <= 0:
        raise ValueError("carga deve ser positiva")
    return (massa(peptideo) + carga * 1.007276) / carga


def espectro_prefixos(peptideo: str) -> list[float]:
    """Massas dos prefixos (só resíduos, sem água), do tamanho 1 ao total."""
    acc, saida = 0.0, []
    for a in peptideo.upper():
        if a not in MASSAS:
            raise ValueError(f"aminoácido inválido: {a!r}")
        acc += MASSAS[a]
        saida.append(acc)
    return saida
