"""Number to LCD Kata: dígitos em estilo display de sete segmentos."""
from __future__ import annotations

# Segmentos: topo, sup-esq, sup-dir, meio, inf-esq, inf-dir, base
_SEGMENTOS = {
    "0": "1110111", "1": "0010010", "2": "1011101", "3": "1011011",
    "4": "0111010", "5": "1101011", "6": "1101111", "7": "1010010",
    "8": "1111111", "9": "1111011",
}


def lcd(numero: str | int, tamanho: int = 1) -> str:
    """Desenha o número; `tamanho` é o comprimento dos traços horizontais/verticais."""
    texto = str(numero)
    if not texto.isdigit():
        raise ValueError("apenas dígitos")
    if tamanho < 1:
        raise ValueError("tamanho deve ser >= 1")
    horiz = lambda ativo: " " + ("-" if ativo else " ") * tamanho + " "

    def lados(esq: bool, dir_: bool) -> str:
        return ("|" if esq else " ") + " " * tamanho + ("|" if dir_ else " ")

    linhas: list[str] = []
    seg = [_SEGMENTOS[d] for d in texto]
    linhas.append(" ".join(horiz(s[0] == "1") for s in seg))
    for _ in range(tamanho):
        linhas.append(" ".join(lados(s[1] == "1", s[2] == "1") for s in seg))
    linhas.append(" ".join(horiz(s[3] == "1") for s in seg))
    for _ in range(tamanho):
        linhas.append(" ".join(lados(s[4] == "1", s[5] == "1") for s in seg))
    linhas.append(" ".join(horiz(s[6] == "1") for s in seg))
    return "\n".join(linhas)
