"""Busca de ORFs (ATG até stop) nas seis fases de leitura."""

from dataclasses import dataclass

from bio_codons import TABELA

_COMP = str.maketrans("ACGT", "TGCA")


@dataclass(frozen=True)
class Orf:
    inicio: int  # índice 0 na fita direta, inclusivo
    fim: int  # exclusivo, inclui o códon de parada
    fita: str  # '+' ou '-'
    proteina: str


def _varrer(seq: str) -> list[tuple[int, int, str]]:
    achados = []
    for fase in range(3):
        i = fase
        while i + 3 <= len(seq):
            if seq[i : i + 3] == "ATG":
                prot = []
                j = i
                while j + 3 <= len(seq):
                    aa = TABELA[seq[j : j + 3]]
                    j += 3
                    if aa == "*":
                        achados.append((i, j, "".join(prot)))
                        i = j - 3
                        break
                    prot.append(aa)
            i += 3
    return achados


def encontrar_orfs(dna: str, min_aa: int = 1) -> list[Orf]:
    """ORFs completos (com stop), sem aninhamento dentro da mesma fase.

    Em fita '-' as coordenadas são convertidas para a fita direta.
    """
    dna = dna.upper()
    if set(dna) - set("ACGT"):
        raise ValueError("DNA inválido")
    n = len(dna)
    saida = []
    for i, j, p in _varrer(dna):
        if len(p) >= min_aa:
            saida.append(Orf(i, j, "+", p))
    rev = dna.translate(_COMP)[::-1]
    for i, j, p in _varrer(rev):
        if len(p) >= min_aa:
            saida.append(Orf(n - j, n - i, "-", p))
    return sorted(saida, key=lambda o: (o.inicio, o.fim, o.fita))
