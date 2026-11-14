"""Word Wrap Kata: quebra de texto em largura máxima."""
from __future__ import annotations


def quebrar(texto: str, largura: int) -> str:
    """Quebra o texto em linhas de no máximo `largura` colunas.

    Prefere quebrar em espaços; palavras maiores que a largura são cortadas.
    """
    if largura < 1:
        raise ValueError("largura deve ser positiva")
    linhas: list[str] = []
    for paragrafo in texto.split("\n"):
        atual = ""
        for palavra in paragrafo.split():
            while len(palavra) > largura:
                if atual:
                    linhas.append(atual)
                    atual = ""
                linhas.append(palavra[:largura])
                palavra = palavra[largura:]
            if not atual:
                atual = palavra
            elif len(atual) + 1 + len(palavra) <= largura:
                atual += " " + palavra
            else:
                linhas.append(atual)
                atual = palavra
        linhas.append(atual)
    return "\n".join(linhas)
