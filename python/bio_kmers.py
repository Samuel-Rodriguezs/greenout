"""Contagem de k-mers."""

from collections import Counter


def contar_kmers(seq: str, k: int) -> Counter:
    """Conta k-mers sobrepostos."""
    if k <= 0:
        raise ValueError("k deve ser positivo")
    return Counter(seq[i : i + k] for i in range(len(seq) - k + 1))


def mais_frequentes(seq: str, k: int) -> list[str]:
    """K-mers com contagem máxima, em ordem alfabética."""
    c = contar_kmers(seq, k)
    if not c:
        return []
    m = max(c.values())
    return sorted(s for s, v in c.items() if v == m)


def kmers_possiveis(k: int, alfabeto: str = "ACGT") -> int:
    return len(set(alfabeto)) ** k


def diversidade(seq: str, k: int) -> float:
    """Fração de k-mers distintos observados sobre os possíveis (ACGT)."""
    return len(contar_kmers(seq, k)) / kmers_possiveis(k)
