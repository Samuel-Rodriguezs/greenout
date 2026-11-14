"""Operações básicas com DNA/RNA: validação, complemento reverso e transcrição."""

DNA = frozenset("ACGT")
RNA = frozenset("ACGU")
_COMP_DNA = str.maketrans("ACGT", "TGCA")
_COMP_RNA = str.maketrans("ACGU", "UGCA")


def validar_dna(seq: str) -> bool:
    """True se a sequência não vazia só tem A, C, G, T (maiúsculas)."""
    return bool(seq) and set(seq) <= DNA


def validar_rna(seq: str) -> bool:
    """True se a sequência não vazia só tem A, C, G, U (maiúsculas)."""
    return bool(seq) and set(seq) <= RNA


def complemento(seq: str, rna: bool = False) -> str:
    """Complemento base a base (sem inverter)."""
    _checar(seq, rna)
    return seq.translate(_COMP_RNA if rna else _COMP_DNA)


def complemento_reverso(seq: str, rna: bool = False) -> str:
    """Complemento reverso: a fita oposta lida de 5' para 3'."""
    return complemento(seq, rna)[::-1]


def transcrever(dna: str) -> str:
    """Transcrição da fita codificante: troca T por U."""
    _checar(dna, False)
    return dna.replace("T", "U")


def transcrever_reversa(rna: str) -> str:
    """Operação inversa: troca U por T."""
    _checar(rna, True)
    return rna.replace("U", "T")


def _checar(seq: str, rna: bool) -> None:
    ok = validar_rna(seq) if rna else validar_dna(seq)
    if not ok and seq != "":
        raise ValueError(f"sequência inválida: {seq!r}")
