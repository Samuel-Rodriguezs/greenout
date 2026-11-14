"""Formatador de tabelas ASCII com alinhamento, truncamento e estilos de borda."""
from __future__ import annotations

import unicodedata
from typing import Any, Sequence


class ErroTabelaAscii(ValueError):
    """Dados inconsistentes para a tabela."""


def largura(texto: str) -> int:
    """Largura de exibição (caracteres largos do Leste Asiático contam 2, combinantes 0)."""
    total = 0
    for c in texto:
        if unicodedata.combining(c):
            continue
        total += 2 if unicodedata.east_asian_width(c) in ("W", "F") else 1
    return total


def _ajustar(texto: str, larg: int, alin: str) -> str:
    falta = larg - largura(texto)
    if alin == "d":
        return " " * falta + texto
    if alin == "c":
        esq = falta // 2
        return " " * esq + texto + " " * (falta - esq)
    return texto + " " * falta


def _truncar(texto: str, maximo: int) -> str:
    if largura(texto) <= maximo:
        return texto
    if maximo <= 1:
        return "…"[:maximo]
    saida = ""
    for c in texto:
        if largura(saida + c) > maximo - 1:
            break
        saida += c
    return saida + "…"


def formatar(cabecalhos: Sequence[str], linhas: Sequence[Sequence[Any]],
             alinhamentos: Sequence[str] | None = None, largura_max: int | None = None,
             estilo: str = "ascii") -> str:
    """Monta a tabela. Alinhamentos: 'e' (esquerda), 'd' (direita), 'c' (centro).

    Por padrão números são alinhados à direita. Estilos: 'ascii' (+-|) ou 'simples' (só traços).
    """
    n = len(cabecalhos)
    if n == 0:
        raise ErroTabelaAscii("é preciso ao menos uma coluna")
    for i, l in enumerate(linhas):
        if len(l) != n:
            raise ErroTabelaAscii(f"linha {i} tem {len(l)} colunas, esperado {n}")
    if alinhamentos is not None:
        if len(alinhamentos) != n or any(a not in ("e", "d", "c") for a in alinhamentos):
            raise ErroTabelaAscii("alinhamentos inválidos")
    elif estilo not in ("ascii", "simples"):
        raise ErroTabelaAscii(f"estilo desconhecido: {estilo}")
    if estilo not in ("ascii", "simples"):
        raise ErroTabelaAscii(f"estilo desconhecido: {estilo}")
    if alinhamentos is None:
        alinhamentos = ["d" if linhas and all(isinstance(l[i], (int, float)) and not isinstance(l[i], bool)
                                              for l in linhas) else "e" for i in range(n)]
    celulas = [[str(c).replace("\n", " ") for c in l] for l in linhas]
    cab = [str(h) for h in cabecalhos]
    larguras = [max([largura(cab[i])] + [largura(l[i]) for l in celulas]) for i in range(n)]
    if largura_max is not None:
        if largura_max < 1:
            raise ErroTabelaAscii("largura_max deve ser positiva")
        larguras = [min(w, largura_max) for w in larguras]
        cab = [_truncar(c, larguras[i]) for i, c in enumerate(cab)]
        celulas = [[_truncar(c, larguras[i]) for i, c in enumerate(l)] for l in celulas]

    def linha(valores: list[str], alins: Sequence[str]) -> str:
        partes = [_ajustar(v, larguras[i], alins[i]) for i, v in enumerate(valores)]
        if estilo == "ascii":
            return "| " + " | ".join(partes) + " |"
        return "  ".join(partes).rstrip()

    if estilo == "ascii":
        borda = "+" + "+".join("-" * (w + 2) for w in larguras) + "+"
        saida = [borda, linha(cab, ["c"] * n), borda]
        saida += [linha(l, alinhamentos) for l in celulas]
        saida.append(borda)
    else:
        saida = [linha(cab, alinhamentos), "  ".join("-" * w for w in larguras)]
        saida += [linha(l, alinhamentos) for l in celulas]
    return "\n".join(saida)
