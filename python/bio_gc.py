"""Conteúdo GC global, em janelas deslizantes e GC skew."""


def conteudo_gc(seq: str) -> float:
    """Fração de G+C (0 a 1). Levanta ValueError se vazia."""
    if not seq:
        raise ValueError("sequência vazia")
    seq = seq.upper()
    return (seq.count("G") + seq.count("C")) / len(seq)


def janelas_gc(seq: str, tamanho: int, passo: int = 1) -> list[tuple[int, float]]:
    """Lista de (início, fração GC) para janelas completas."""
    if tamanho <= 0 or passo <= 0:
        raise ValueError("tamanho e passo devem ser positivos")
    return [
        (i, conteudo_gc(seq[i : i + tamanho]))
        for i in range(0, len(seq) - tamanho + 1, passo)
    ]


def gc_skew(seq: str) -> float:
    """(G - C) / (G + C); 0.0 se não houver G nem C."""
    seq = seq.upper()
    g, c = seq.count("G"), seq.count("C")
    return 0.0 if g + c == 0 else (g - c) / (g + c)


def janela_mais_rica(seq: str, tamanho: int) -> tuple[int, float]:
    """Primeira janela com maior GC."""
    js = janelas_gc(seq, tamanho)
    if not js:
        raise ValueError("sequência menor que a janela")
    return max(js, key=lambda t: (t[1], -t[0]))
