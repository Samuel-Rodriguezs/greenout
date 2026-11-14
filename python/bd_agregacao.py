"""Agregações e GROUP BY/HAVING como operador Volcano (agrupamento por hash).

COUNT(*), COUNT(x), SUM, AVG, MIN, MAX ignoram NULLs (exceto COUNT(*)). Sem GROUP BY,
a entrada vira um único grupo: sobre entrada vazia, COUNT dá 0 e os demais NULL.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional, Sequence

from bd_sql_parser import (AGREGADOS, Binario, Chamada, Coluna, EhNulo, EmLista, Entre,
                           Literal, Unario, contem_agregado)
from bd_volcano import ErroExecucao, Operador, avaliar, resolver


def calcular_agregado(nome: str, valores: Sequence[Any], estrela: bool = False) -> Any:
    if nome == "COUNT":
        return len(valores) if estrela else sum(1 for v in valores if v is not None)
    uteis = [v for v in valores if v is not None]
    if not uteis:
        return None
    if nome == "SUM":
        return sum(uteis)
    if nome == "AVG":
        return sum(uteis) / len(uteis)
    if nome == "MIN":
        return min(uteis)
    if nome == "MAX":
        return max(uteis)
    raise ErroExecucao(f"agregado desconhecido: {nome}")


def _substituir(expr: Any, esquema, grupo: list[tuple]) -> Any:
    """Troca cada agregado da expressão por Literal com seu valor no grupo."""
    if isinstance(expr, Chamada):
        if expr.nome in AGREGADOS:
            if expr.estrela:
                return Literal(calcular_agregado("COUNT", grupo, True))
            arg = expr.args[0]
            if contem_agregado(arg):
                raise ErroExecucao("agregados aninhados não são permitidos")
            vals = [avaliar(arg, esquema, l) for l in grupo]
            return Literal(calcular_agregado(expr.nome, vals))
        return Chamada(expr.nome, tuple(_substituir(a, esquema, grupo) for a in expr.args))
    if isinstance(expr, Binario):
        return Binario(expr.op, _substituir(expr.esq, esquema, grupo), _substituir(expr.dir, esquema, grupo))
    if isinstance(expr, Unario):
        return Unario(expr.op, _substituir(expr.expr, esquema, grupo))
    if isinstance(expr, EhNulo):
        return replace(expr, expr=_substituir(expr.expr, esquema, grupo))
    if isinstance(expr, EmLista):
        return EmLista(_substituir(expr.expr, esquema, grupo),
                       tuple(_substituir(i, esquema, grupo) for i in expr.itens), expr.negado)
    if isinstance(expr, Entre):
        return Entre(*(_substituir(x, esquema, grupo) for x in (expr.expr, expr.lo, expr.hi)), expr.negado)
    return expr


def _colunas_livres(expr: Any) -> list[Coluna]:
    """Colunas citadas fora de agregados."""
    if isinstance(expr, Coluna):
        return [expr]
    if isinstance(expr, Chamada):
        return [] if expr.nome in AGREGADOS else [c for a in expr.args for c in _colunas_livres(a)]
    if isinstance(expr, Binario):
        return _colunas_livres(expr.esq) + _colunas_livres(expr.dir)
    if isinstance(expr, (Unario, EhNulo)):
        return _colunas_livres(expr.expr)
    if isinstance(expr, EmLista):
        return _colunas_livres(expr.expr) + [c for i in expr.itens for c in _colunas_livres(i)]
    if isinstance(expr, Entre):
        return [c for x in (expr.expr, expr.lo, expr.hi) for c in _colunas_livres(x)]
    return []


class Agrupamento(Operador):
    def __init__(self, filho: Operador, chaves: Sequence[Any], saidas: Sequence[tuple[Any, str]],
                 having: Any = None) -> None:
        self.filho = filho
        self.chaves = list(chaves)
        self.saidas = list(saidas)
        self.having = having
        self.esquema = [("", nome.lower()) for _, nome in self.saidas]
        self._validar()
        self._linhas: list[tuple] = []
        self._i = 0

    def _validar(self) -> None:
        esq = self.filho.esquema
        permitidas = {resolver(esq, c) for c in self.chaves if isinstance(c, Coluna)}
        exprs = [e for e, _ in self.saidas] + ([self.having] if self.having is not None else [])
        for e in exprs:
            for c in _colunas_livres(e):
                if resolver(esq, c) not in permitidas and not any(e == k for k in self.chaves):
                    raise ErroExecucao(f"coluna {c.nome!r} deve estar no GROUP BY ou em um agregado")

    def abrir(self) -> None:
        esq = self.filho.esquema
        grupos: dict[tuple, list[tuple]] = {}
        for linha in self.filho:
            chave = tuple(avaliar(k, esq, linha) for k in self.chaves)
            grupos.setdefault(chave, []).append(linha)
        if not self.chaves and not grupos:
            grupos[()] = []
        saida = []
        for grupo in grupos.values():
            rep = grupo[0] if grupo else (None,) * len(esq)
            if self.having is not None:
                h = avaliar(_substituir(self.having, esq, grupo), esq, rep)
                if h is not True:
                    continue
            saida.append(tuple(avaliar(_substituir(e, esq, grupo), esq, rep) for e, _ in self.saidas))
        self._linhas, self._i = saida, 0

    def proximo(self) -> Optional[tuple]:
        if self._i >= len(self._linhas):
            return None
        self._i += 1
        return self._linhas[self._i - 1]

    def fechar(self) -> None:
        self._linhas = []
