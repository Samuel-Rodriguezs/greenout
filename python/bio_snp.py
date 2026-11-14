"""Detecção de SNPs entre sequências e efeito sobre o códon."""

from bio_codons import TABELA


def encontrar_snps(ref: str, alt: str) -> list[tuple[int, str, str]]:
    """(posição base 1, base ref, base alt) para cada diferença."""
    if len(ref) != len(alt):
        raise ValueError("sequências com tamanhos diferentes")
    return [(i + 1, r, a) for i, (r, a) in enumerate(zip(ref, alt)) if r != a]


def efeito(cds: str, posicao: int, novo: str) -> str:
    """Classifica uma substituição (posição base 1) na CDS.

    Retorna 'sinonima', 'missense' ou 'nonsense'.
    """
    if not 1 <= posicao <= len(cds):
        raise ValueError("posição fora da CDS")
    if len(novo) != 1 or novo not in "ACGT":
        raise ValueError("base inválida")
    i = (posicao - 1) // 3 * 3
    cod = cds[i : i + 3]
    if len(cod) < 3:
        raise ValueError("códon incompleto")
    k = (posicao - 1) - i
    mut = cod[:k] + novo + cod[k + 1 :]
    a, b = TABELA[cod], TABELA[mut]
    if a == b:
        return "sinonima"
    return "nonsense" if b == "*" else "missense"
