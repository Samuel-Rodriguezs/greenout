"""Quebra de linha (word wrap) e justificação de texto."""


def _palavras(texto: str, largura: int) -> list[str]:
    if largura < 1:
        raise ValueError("largura deve ser >= 1")
    saida = []
    for p in texto.split():
        while len(p) > largura:  # palavra maior que a linha: quebra à força
            saida.append(p[:largura])
            p = p[largura:]
        saida.append(p)
    return saida


def quebrar_linhas(texto: str, largura: int) -> list[str]:
    """Quebra gulosa em linhas de no máximo `largura` caracteres."""
    linhas: list[str] = []
    atual = ""
    for p in _palavras(texto, largura):
        if not atual:
            atual = p
        elif len(atual) + 1 + len(p) <= largura:
            atual += " " + p
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def _justificar_linha(linha: str, largura: int) -> str:
    palavras = linha.split(" ")
    if len(palavras) == 1:
        return linha
    espacos = largura - sum(len(p) for p in palavras)
    lacunas = len(palavras) - 1
    base, resto = divmod(espacos, lacunas)
    partes = []
    for i, p in enumerate(palavras[:-1]):
        partes.append(p + " " * (base + (1 if i < resto else 0)))
    partes.append(palavras[-1])
    return "".join(partes)


def justificar(texto: str, largura: int) -> list[str]:
    """Justifica nas duas margens; a última linha fica alinhada à esquerda."""
    linhas = quebrar_linhas(texto, largura)
    return [_justificar_linha(l, largura) for l in linhas[:-1]] + linhas[-1:]


def centralizar(texto: str, largura: int) -> list[str]:
    return [l.center(largura).rstrip() for l in quebrar_linhas(texto, largura)]
