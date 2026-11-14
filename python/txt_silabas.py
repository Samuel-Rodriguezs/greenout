"""Divisão e contagem de sílabas de palavras em português (regras simplificadas)."""

_VOGAIS = set("aeiouáéíóúâêôãõàü")
_FRACAS = set("iuü")
_GRUPOS_INSEPARAVEIS = {
    "bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "tl", "tr", "vr",
    "ch", "lh", "nh",
}


def _eh_vogal(p: str, i: int) -> bool:
    c = p[i]
    if c not in _VOGAIS:
        return False
    # 'u' mudo em que/qui/gue/gui
    if c == "u" and i > 0 and p[i - 1] in "qg" and i + 1 < len(p) and p[i + 1] in "eiéêíè":
        return False
    return True


def _junta(a: str, b: str) -> bool:
    """Duas vogais vizinhas ficam na mesma sílaba (ditongo)?"""
    if b in "íú":
        return False
    if a in "ãõ":
        return True
    return a in _FRACAS or b in _FRACAS


def dividir_silabas(palavra: str) -> list[str]:
    p = "".join(c for c in palavra.lower() if c.isalpha())
    if not p:
        return []
    nucleos: list[list[int]] = []
    for i in range(len(p)):
        if not _eh_vogal(p, i):
            continue
        if nucleos and nucleos[-1][1] == i and _junta(p[i - 1], p[i]):
            nucleos[-1][1] = i + 1
        else:
            nucleos.append([i, i + 1])
    if not nucleos:
        return [p]
    cortes = []
    for k in range(len(nucleos) - 1):
        lacuna = p[nucleos[k][1]:nucleos[k + 1][0]]
        n = len(lacuna)
        if n >= 2 and lacuna[-2:] in _GRUPOS_INSEPARAVEIS:
            corte = n - 2
        else:
            corte = max(n - 1, 0)
        cortes.append(nucleos[k][1] + corte)
    pontos = [0] + cortes + [len(p)]
    return [p[pontos[i]:pontos[i + 1]] for i in range(len(pontos) - 1)]


def contar_silabas(palavra: str) -> int:
    return len(dividir_silabas(palavra))
