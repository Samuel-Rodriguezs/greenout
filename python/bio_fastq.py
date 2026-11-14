"""Parser de FASTQ e qualidade Phred+33."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Leitura:
    id: str
    sequencia: str
    qualidade: str

    def phred(self) -> list[int]:
        return decodificar(self.qualidade)


def decodificar(qual: str, offset: int = 33) -> list[int]:
    """Converte caracteres ASCII em escores Phred."""
    escores = [ord(c) - offset for c in qual]
    if any(q < 0 for q in escores):
        raise ValueError("caractere de qualidade abaixo do offset")
    return escores


def prob_erro(q: int) -> float:
    """Probabilidade de erro: 10^(-Q/10)."""
    return 10 ** (-q / 10)


def parse(texto: str) -> list[Leitura]:
    linhas = [l.rstrip("\r") for l in texto.split("\n")]
    while linhas and linhas[-1] == "":
        linhas.pop()
    if len(linhas) % 4:
        raise ValueError("FASTQ incompleto: número de linhas não múltiplo de 4")
    leituras = []
    for i in range(0, len(linhas), 4):
        cab, seq, mais, qual = linhas[i : i + 4]
        if not cab.startswith("@") or not mais.startswith("+"):
            raise ValueError(f"formato inválido perto da linha {i + 1}")
        if len(seq) != len(qual):
            raise ValueError(f"sequência e qualidade com tamanhos diferentes: {cab}")
        leituras.append(Leitura(cab[1:].split(" ")[0], seq, qual))
    return leituras


def qualidade_media(leitura: Leitura) -> float:
    q = leitura.phred()
    if not q:
        raise ValueError("leitura vazia")
    return sum(q) / len(q)


def aparar_fim(leitura: Leitura, minimo: int) -> Leitura:
    """Remove bases do fim enquanto a qualidade for menor que ``minimo``."""
    q = leitura.phred()
    n = len(q)
    while n > 0 and q[n - 1] < minimo:
        n -= 1
    return Leitura(leitura.id, leitura.sequencia[:n], leitura.qualidade[:n])
