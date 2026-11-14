"""Tabela do código genético padrão e tradução de sequências."""

_BASES = "TCAG"
_AAS = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"

TABELA: dict[str, str] = {
    a + b + c: _AAS[16 * i + 4 * j + k]
    for i, a in enumerate(_BASES)
    for j, b in enumerate(_BASES)
    for k, c in enumerate(_BASES)
}


def traduzir(seq: str, ate_stop: bool = True) -> str:
    """Traduz DNA ou RNA em proteína (U é tratado como T).

    Códon final incompleto é ignorado. Com ``ate_stop`` a tradução termina no
    primeiro stop (que não aparece); senão o stop vira '*'.
    """
    seq = seq.upper().replace("U", "T")
    prot = []
    for i in range(0, len(seq) - len(seq) % 3, 3):
        cod = seq[i : i + 3]
        if cod not in TABELA:
            raise ValueError(f"códon inválido: {cod!r}")
        aa = TABELA[cod]
        if aa == "*" and ate_stop:
            break
        prot.append(aa)
    return "".join(prot)


def codons_sinonimos(aa: str) -> list[str]:
    """Códons (DNA, ordem alfabética) que codificam o aminoácido (ou '*')."""
    return sorted(c for c, a in TABELA.items() if a == aa)
