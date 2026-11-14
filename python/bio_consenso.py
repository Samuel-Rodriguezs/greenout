"""Sequência consenso de um alinhamento (maioria ou código IUPAC)."""

from collections import Counter

IUPAC = {
    "A": "A", "C": "C", "G": "G", "T": "T", "AG": "R", "CT": "Y", "CG": "S",
    "AT": "W", "GT": "K", "AC": "M", "CGT": "B", "AGT": "D", "ACT": "H",
    "ACG": "V", "ACGT": "N",
}


def _colunas(alin: list[str]) -> list[Counter]:
    if not alin or not alin[0] or any(len(s) != len(alin[0]) for s in alin):
        raise ValueError("alinhamento vazio ou com tamanhos diferentes")
    return [Counter(s[i] for s in alin) for i in range(len(alin[0]))]


def consenso(alin: list[str]) -> str:
    """Base mais frequente por coluna; empate resolvido em ordem alfabética."""
    return "".join(min(c, key=lambda b: (-c[b], b)) for c in _colunas(alin))


def consenso_iupac(alin: list[str], limiar: float = 0.3) -> str:
    """Código IUPAC com as bases cuja frequência é >= ``limiar``."""
    n = len(alin)
    saida = []
    for c in _colunas(alin):
        bases = "".join(sorted(b for b in c if c[b] / n >= limiar and b in "ACGT"))
        saida.append(IUPAC[bases or "ACGT"])
    return "".join(saida)
