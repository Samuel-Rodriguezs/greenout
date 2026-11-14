"""Executor estilo Volcano: operadores com abrir()/proximo()/fechar() e avaliador de expressões.

Uma linha é uma tupla; o esquema de um operador é uma lista de (tabela, coluna) em minúsculas.
Lógica de três valores: None representa UNKNOWN/NULL.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Iterable, Iterator, Optional, Sequence

from bd_sql_parser import (AGREGADOS, Binario, Chamada, Coluna, EhNulo, EmLista, Entre,
                           Literal, Unario)

Esquema = list[tuple[str, str]]


class ErroExecucao(Exception):
    pass


def resolver(esquema: Esquema, col: Coluna) -> int:
    nome = col.nome.lower()
    tab = col.tabela.lower() if col.tabela else None
    achados = [i for i, (t, c) in enumerate(esquema) if c == nome and (tab is None or t == tab)]
    if not achados:
        raise ErroExecucao(f"coluna inexistente: {(tab + '.') if tab else ''}{nome}")
    if len(achados) > 1:
        raise ErroExecucao(f"coluna ambígua: {nome}")
    return achados[0]


def _like(valor: str, padrao: str) -> bool:
    rx = "".join(".*" if ch == "%" else "." if ch == "_" else re.escape(ch) for ch in padrao)
    return re.fullmatch(rx, valor, re.DOTALL) is not None


def _comparar(op: str, a: Any, b: Any) -> Optional[bool]:
    if a is None or b is None:
        return None
    if isinstance(a, str) != isinstance(b, str):
        raise ErroExecucao(f"não é possível comparar {a!r} com {b!r}")
    return {"=": a == b, "<>": a != b, "<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op]


def avaliar(expr: Any, esquema: Esquema, linha: Sequence[Any]) -> Any:
    if isinstance(expr, Literal):
        return expr.valor
    if isinstance(expr, Coluna):
        return linha[resolver(esquema, expr)]
    if isinstance(expr, Unario):
        v = avaliar(expr.expr, esquema, linha)
        if v is None:
            return None
        if expr.op == "NOT":
            return not v
        return -v
    if isinstance(expr, EhNulo):
        r = avaliar(expr.expr, esquema, linha) is None
        return (not r) if expr.negado else r
    if isinstance(expr, Binario):
        if expr.op == "AND":
            a = avaliar(expr.esq, esquema, linha)
            if a is False:
                return False
            b = avaliar(expr.dir, esquema, linha)
            if b is False:
                return False
            return None if a is None or b is None else True
        if expr.op == "OR":
            a = avaliar(expr.esq, esquema, linha)
            if a is True:
                return True
            b = avaliar(expr.dir, esquema, linha)
            if b is True:
                return True
            return None if a is None or b is None else False
        a = avaliar(expr.esq, esquema, linha)
        b = avaliar(expr.dir, esquema, linha)
        if expr.op in ("=", "<>", "<", "<=", ">", ">="):
            return _comparar(expr.op, a, b)
        if a is None or b is None:
            return None
        if expr.op == "LIKE":
            if not isinstance(a, str) or not isinstance(b, str):
                raise ErroExecucao("LIKE exige texto")
            return _like(a, b)
        if isinstance(a, str) or isinstance(b, str):
            if expr.op == "+" and isinstance(a, str) and isinstance(b, str):
                return a + b
            raise ErroExecucao(f"operador {expr.op} inválido para texto")
        if expr.op == "+":
            return a + b
        if expr.op == "-":
            return a - b
        if expr.op == "*":
            return a * b
        if b == 0:
            raise ErroExecucao("divisão por zero")
        if expr.op == "/":
            return a // b if isinstance(a, int) and isinstance(b, int) else a / b
        if expr.op == "%":
            return a % b
        raise ErroExecucao(f"operador desconhecido: {expr.op}")
    if isinstance(expr, EmLista):
        v = avaliar(expr.expr, esquema, linha)
        if v is None:
            return None
        itens = [avaliar(i, esquema, linha) for i in expr.itens]
        if v in [i for i in itens if i is not None]:
            r: Optional[bool] = True
        else:
            r = None if any(i is None for i in itens) else False
        return r if r is None or not expr.negado else not r
    if isinstance(expr, Entre):
        v, lo, hi = (avaliar(x, esquema, linha) for x in (expr.expr, expr.lo, expr.hi))
        a, b = _comparar(">=", v, lo), _comparar("<=", v, hi)
        r = False if (a is False or b is False) else (None if a is None or b is None else True)
        return r if r is None or not expr.negado else not r
    if isinstance(expr, Chamada):
        if expr.nome in AGREGADOS:
            raise ErroExecucao(f"agregado {expr.nome} fora de contexto de agrupamento")
        args = [avaliar(a, esquema, linha) for a in expr.args]
        return _funcao(expr.nome, args)
    raise ErroExecucao(f"expressão não suportada: {expr!r}")


def _funcao(nome: str, args: list[Any]) -> Any:
    if nome == "COALESCE":
        return next((a for a in args if a is not None), None)
    if len(args) != 1:
        raise ErroExecucao(f"{nome} espera 1 argumento")
    v = args[0]
    if v is None:
        return None
    if nome == "UPPER":
        return v.upper()
    if nome == "LOWER":
        return v.lower()
    if nome == "LENGTH":
        return len(v)
    if nome == "ABS":
        return abs(v)
    raise ErroExecucao(f"função desconhecida: {nome}")


# ---------------- operadores ----------------
class Operador:
    esquema: Esquema

    def abrir(self) -> None: ...
    def proximo(self) -> Optional[tuple]: ...
    def fechar(self) -> None: ...

    def __iter__(self) -> Iterator[tuple]:
        self.abrir()
        try:
            while (linha := self.proximo()) is not None:
                yield linha
        finally:
            self.fechar()

    def todas(self) -> list[tuple]:
        return list(self)


class Scan(Operador):
    def __init__(self, tabela: str, colunas: Sequence[str], linhas: Iterable[Sequence[Any]],
                 alias: Optional[str] = None) -> None:
        nome = (alias or tabela).lower()
        self.esquema = [(nome, c.lower()) for c in colunas]
        self._fonte = linhas
        self._it: Optional[Iterator] = None
        self.lidas = 0

    def abrir(self) -> None:
        self._it = iter(self._fonte)

    def proximo(self) -> Optional[tuple]:
        if self._it is None:
            raise ErroExecucao("operador não aberto")
        for linha in self._it:
            self.lidas += 1
            return tuple(linha)
        return None

    def fechar(self) -> None:
        self._it = None


class Filtro(Operador):
    def __init__(self, filho: Operador, predicado: Any) -> None:
        self.filho, self.predicado = filho, predicado
        self.esquema = filho.esquema

    def abrir(self) -> None:
        self.filho.abrir()

    def proximo(self) -> Optional[tuple]:
        while (linha := self.filho.proximo()) is not None:
            if avaliar(self.predicado, self.esquema, linha) is True:  # UNKNOWN descarta
                return linha
        return None

    def fechar(self) -> None:
        self.filho.fechar()


class Projecao(Operador):
    def __init__(self, filho: Operador, itens: Sequence[tuple[Any, str]]) -> None:
        """itens: pares (expressão, nome_de_saída)."""
        self.filho = filho
        self.itens = list(itens)
        self.esquema = [("", nome.lower()) for _, nome in self.itens]

    def abrir(self) -> None:
        self.filho.abrir()

    def proximo(self) -> Optional[tuple]:
        linha = self.filho.proximo()
        if linha is None:
            return None
        return tuple(avaliar(e, self.filho.esquema, linha) for e, _ in self.itens)

    def fechar(self) -> None:
        self.filho.fechar()


class JuncaoLoopAninhado(Operador):
    """Junção interna por laço aninhado (condição opcional = produto cartesiano)."""

    def __init__(self, esq: Operador, dir: Operador, condicao: Any = None) -> None:
        self.esq, self.dir, self.condicao = esq, dir, condicao
        self.esquema = esq.esquema + dir.esquema
        self._direita: list[tuple] = []
        self._atual: Optional[tuple] = None
        self._i = 0

    def abrir(self) -> None:
        self.esq.abrir()
        self._direita = self.dir.todas()  # materializa o lado interno uma vez
        self._atual, self._i = None, 0

    def proximo(self) -> Optional[tuple]:
        while True:
            if self._atual is None:
                self._atual = self.esq.proximo()
                self._i = 0
                if self._atual is None:
                    return None
            while self._i < len(self._direita):
                junta = self._atual + self._direita[self._i]
                self._i += 1
                if self.condicao is None or avaliar(self.condicao, self.esquema, junta) is True:
                    return junta
            self._atual = None

    def fechar(self) -> None:
        self.esq.fechar()
        self._direita = []


class Limite(Operador):
    def __init__(self, filho: Operador, n: int, deslocamento: int = 0) -> None:
        if n < 0 or deslocamento < 0:
            raise ErroExecucao("limite/deslocamento negativo")
        self.filho, self.n, self.desloc = filho, n, deslocamento
        self.esquema = filho.esquema
        self._emitidas = 0

    def abrir(self) -> None:
        self.filho.abrir()
        self._emitidas = 0
        for _ in range(self.desloc):
            if self.filho.proximo() is None:
                break

    def proximo(self) -> Optional[tuple]:
        if self._emitidas >= self.n:
            return None  # curto-circuito: não puxa mais linhas do filho
        linha = self.filho.proximo()
        if linha is not None:
            self._emitidas += 1
        return linha

    def fechar(self) -> None:
        self.filho.fechar()


class Distinto(Operador):
    def __init__(self, filho: Operador) -> None:
        self.filho = filho
        self.esquema = filho.esquema
        self._vistas: set = set()

    def abrir(self) -> None:
        self.filho.abrir()
        self._vistas = set()

    def proximo(self) -> Optional[tuple]:
        while (linha := self.filho.proximo()) is not None:
            if linha not in self._vistas:
                self._vistas.add(linha)
                return linha
        return None

    def fechar(self) -> None:
        self.filho.fechar()


class Ordenacao(Operador):
    """ORDER BY em memória; NULLs primeiro em ASC. chaves: (expr, desc)."""

    def __init__(self, filho: Operador, chaves: Sequence[tuple[Any, bool]]) -> None:
        self.filho, self.chaves = filho, list(chaves)
        self.esquema = filho.esquema
        self._buf: list[tuple] = []
        self._i = 0

    def abrir(self) -> None:
        self.filho.abrir()
        linhas = []
        while (l := self.filho.proximo()) is not None:
            linhas.append(l)
        for expr, desc in reversed(self.chaves):  # sort estável, da última chave para a primeira
            linhas.sort(key=lambda l: _chave(avaliar(expr, self.esquema, l)), reverse=desc)
        self._buf, self._i = linhas, 0

    def proximo(self) -> Optional[tuple]:
        if self._i >= len(self._buf):
            return None
        self._i += 1
        return self._buf[self._i - 1]

    def fechar(self) -> None:
        self.filho.fechar()
        self._buf = []


def _chave(v: Any) -> tuple:
    return (0, 0) if v is None else (1, v)
