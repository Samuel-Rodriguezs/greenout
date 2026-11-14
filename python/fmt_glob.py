"""Glob matcher próprio: *, ?, [a-z], [!x] e **, sem usar fnmatch/re."""
from __future__ import annotations


class ErroGlob(ValueError):
    """Padrão glob inválido."""


def _classe(padrao: str, i: int) -> tuple[list[tuple[str, str]], bool, int]:
    """Lê uma classe a partir de padrao[i] == '['. Retorna (faixas, negada, próximo índice)."""
    j = i + 1
    negada = False
    if j < len(padrao) and padrao[j] in "!^":
        negada = True
        j += 1
    faixas: list[tuple[str, str]] = []
    primeiro = True
    while j < len(padrao):
        c = padrao[j]
        if c == "]" and not primeiro:
            return faixas, negada, j + 1
        primeiro = False
        if c == "\\" and j + 1 < len(padrao):
            j += 1
            c = padrao[j]
        if j + 2 < len(padrao) and padrao[j + 1] == "-" and padrao[j + 2] != "]":
            fim = padrao[j + 2]
            if fim < c:
                raise ErroGlob(f"faixa invertida: {c}-{fim}")
            faixas.append((c, fim))
            j += 3
        else:
            faixas.append((c, c))
            j += 1
    raise ErroGlob("classe '[' não fechada")


def _casa(padrao: str, texto: str, pi: int, ti: int, sep: bool, memo: dict) -> bool:
    chave = (pi, ti)
    if chave in memo:
        return memo[chave]
    while True:
        if pi == len(padrao):
            r = ti == len(texto)
            break
        c = padrao[pi]
        if c == "*":
            duplo = sep and padrao[pi:pi + 2] == "**"
            prox = pi
            while prox < len(padrao) and padrao[prox] == "*":
                prox += 1
            if duplo:
                # ** atravessa '/'; "**/" também casa zero diretórios
                alt = prox + 1 if padrao[prox:prox + 1] == "/" else prox
                r = any(_casa(padrao, texto, alt, k, sep, memo) for k in range(ti, len(texto) + 1)) or \
                    any(_casa(padrao, texto, prox, k, sep, memo) for k in range(ti, len(texto) + 1))
            else:
                r = False
                for k in range(ti, len(texto) + 1):
                    if _casa(padrao, texto, prox, k, sep, memo):
                        r = True
                        break
                    if k < len(texto) and sep and texto[k] == "/":
                        break
            break
        if ti >= len(texto):
            r = False
            break
        t = texto[ti]
        if c == "?":
            if sep and t == "/":
                r = False
                break
            pi += 1
            ti += 1
        elif c == "[":
            faixas, negada, prox = _classe(padrao, pi)
            dentro = any(a <= t <= b for a, b in faixas)
            if dentro == negada or (sep and t == "/"):
                r = False
                break
            pi, ti = prox, ti + 1
        else:
            if c == "\\" and pi + 1 < len(padrao):
                pi += 1
                c = padrao[pi]
            if c != t:
                r = False
                break
            pi += 1
            ti += 1
    memo[chave] = r
    return r


def casa(padrao: str, texto: str, caminho: bool = False) -> bool:
    """Retorna True se `texto` casa com `padrao`.

    Com caminho=True, '*' e '?' não atravessam '/', e '**' atravessa.
    """
    _validar(padrao)
    return _casa(padrao, texto, 0, 0, caminho, {})


def _validar(padrao: str) -> None:
    i = 0
    while i < len(padrao):
        if padrao[i] == "\\":
            i += 2
        elif padrao[i] == "[":
            i = _classe(padrao, i)[2]
        else:
            i += 1


def filtrar(padrao: str, nomes: list[str], caminho: bool = False) -> list[str]:
    return [n for n in nomes if casa(padrao, n, caminho)]
