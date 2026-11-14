"""Parser de tabelas Markdown (estilo GFM) para lista de dicionários."""
from __future__ import annotations


class ErroTabela(ValueError):
    """Tabela Markdown malformada."""


def _celulas(linha: str) -> list[str]:
    s = linha.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    celulas: list[str] = []
    atual: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            atual.append("|")
            i += 2
            continue
        if c == "|":
            celulas.append("".join(atual).strip())
            atual = []
        else:
            atual.append(c)
        i += 1
    celulas.append("".join(atual).strip())
    return celulas


def _alinhamento(celula: str) -> str:
    c = celula.strip()
    if not c or set(c) - set(":-") or "-" not in c:
        raise ErroTabela(f"separador inválido: {celula!r}")
    esq, dir_ = c.startswith(":"), c.endswith(":")
    if esq and dir_:
        return "centro"
    if dir_:
        return "direita"
    return "esquerda"


def parse_tabela(texto: str) -> tuple[list[str], list[str], list[dict[str, str]]]:
    """Retorna (cabeçalhos, alinhamentos, linhas como dicionários)."""
    linhas = [l for l in texto.strip().splitlines() if l.strip()]
    if len(linhas) < 2:
        raise ErroTabela("tabela precisa de cabeçalho e separador")
    cab = _celulas(linhas[0])
    if any(not h for h in cab):
        raise ErroTabela("cabeçalho vazio")
    sep = _celulas(linhas[1])
    if len(sep) != len(cab):
        raise ErroTabela("separador com número de colunas diferente do cabeçalho")
    alin = [_alinhamento(c) for c in sep]
    registros: list[dict[str, str]] = []
    for n, l in enumerate(linhas[2:], start=3):
        cel = _celulas(l)
        if len(cel) > len(cab):
            raise ErroTabela(f"linha {n} com colunas demais")
        cel += [""] * (len(cab) - len(cel))
        registros.append(dict(zip(cab, cel)))
    return cab, alin, registros


def para_dicts(texto: str) -> list[dict[str, str]]:
    return parse_tabela(texto)[2]


def _pad(txt: str, larg: int, alin: str) -> str:
    if alin == "direita":
        return txt.rjust(larg)
    if alin == "centro":
        return txt.center(larg)
    return txt.ljust(larg)


def gerar_tabela(cabecalhos: list[str], linhas: list[list[str]], alinhamentos: list[str] | None = None) -> str:
    """Gera uma tabela Markdown com colunas alinhadas."""
    alinhamentos = alinhamentos or ["esquerda"] * len(cabecalhos)
    esc = lambda t: str(t).replace("|", "\\|")
    todas = [[esc(h) for h in cabecalhos]] + [[esc(c) for c in l] for l in linhas]
    for l in todas:
        if len(l) != len(cabecalhos):
            raise ErroTabela("linha com número de colunas incorreto")
    larg = [max(3, max(len(l[i]) for l in todas)) for i in range(len(cabecalhos))]
    def fmt(l: list[str]) -> str:
        return "| " + " | ".join(_pad(c, larg[i], alinhamentos[i]) for i, c in enumerate(l)) + " |"
    marcas = []
    for i, a in enumerate(alinhamentos):
        w = larg[i]
        marcas.append(":" + "-" * (w - 2) + ":" if a == "centro" else
                      "-" * (w - 1) + ":" if a == "direita" else "-" * w)
    saida = [fmt(todas[0]), "| " + " | ".join(marcas) + " |"]
    saida += [fmt(l) for l in todas[1:]]
    return "\n".join(saida)
