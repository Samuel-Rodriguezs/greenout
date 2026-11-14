"""Stemmer simples de sufixos para o português."""

_SUFIXOS = sorted([
    "amentos", "imentos", "amento", "imento", "adoras", "adores", "ações", "idades",
    "mente", "ação", "ador", "adora", "idade", "ismo", "ista", "ável", "ível",
    "osos", "osas", "oso", "osa", "ando", "endo", "indo", "ados", "adas", "idos", "idas",
    "ado", "ada", "ido", "ida", "inho", "inha", "zinho", "zinha", "ões", "ão", "es", "as", "os",
    "ar", "er", "ir", "a", "e", "o", "s",
], key=len, reverse=True)


def stem(palavra: str, minimo: int = 3) -> str:
    """Remove o maior sufixo conhecido mantendo ao menos `minimo` letras de radical."""
    p = palavra.lower()
    for suf in _SUFIXOS:
        if p.endswith(suf) and len(p) - len(suf) >= minimo:
            return p[: -len(suf)]
    return p


def stem_todos(palavras: list[str]) -> list[str]:
    return [stem(p) for p in palavras]
