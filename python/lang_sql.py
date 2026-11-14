"""Mini-SQL: SELECT cols FROM tabela [WHERE cond] [ORDER BY col [ASC|DESC]] [LIMIT n] sobre listas de dicts.

WHERE aceita comparações (=, !=, <>, <, <=, >, >=), LIKE (% e _), IN (...), IS [NOT] NULL,
AND, OR, NOT e parênteses.
"""
from __future__ import annotations

import re
from typing import Any, Callable

from lang_tokenizer import ErroLexico, Token, Tokenizador

Linha = dict[str, Any]
Banco = dict[str, list[Linha]]


class ErroSQL(Exception):
    """Erro de sintaxe ou execução."""


_TOK = Tokenizador([
    ("NUM", r"-?\d+(?:\.\d+)?"),
    ("STR", r"'(?:[^']|'')*'"),
    ("ID", r"[A-Za-z_][\w.]*"),
    ("OP", r"<=|>=|<>|!=|[=<>(),*]"),
    ("ESPACO", r"\s+"),
])
_RESERVADAS = {"SELECT", "FROM", "WHERE", "ORDER", "BY", "LIMIT", "AND", "OR", "NOT", "LIKE",
               "IN", "IS", "NULL", "ASC", "DESC", "TRUE", "FALSE"}


class _P:
    def __init__(self, texto: str) -> None:
        try:
            self.t: list[Token] = list(_TOK.tokenizar(texto))
        except ErroLexico as e:
            raise ErroSQL(str(e)) from None
        self.i = 0

    def prox(self) -> Token | None:
        return self.t[self.i] if self.i < len(self.t) else None

    def kw(self, *palavras: str) -> bool:
        t = self.prox()
        return t is not None and t.tipo == "ID" and t.valor.upper() in palavras

    def op(self, *ops: str) -> bool:
        t = self.prox()
        return t is not None and t.tipo == "OP" and t.valor in ops

    def exige_kw(self, p: str) -> None:
        if not self.kw(p):
            t = self.prox()
            raise ErroSQL(f"esperado {p}, encontrado {t.valor if t else 'fim'!r}")
        self.i += 1

    def exige_op(self, o: str) -> None:
        if not self.op(o):
            t = self.prox()
            raise ErroSQL(f"esperado {o!r}, encontrado {t.valor if t else 'fim'!r}")
        self.i += 1

    def identificador(self) -> str:
        t = self.prox()
        if t is None or t.tipo != "ID" or t.valor.upper() in _RESERVADAS:
            raise ErroSQL(f"identificador esperado, encontrado {t.valor if t else 'fim'!r}")
        self.i += 1
        return t.valor

    # ---- condições ----
    def condicao(self) -> Callable[[Linha], bool]:
        esq = self.e()
        while self.kw("OR"):
            self.i += 1
            dir_ = self.e()
            esq = (lambda a, b: lambda r: a(r) or b(r))(esq, dir_)
        return esq

    def e(self) -> Callable[[Linha], bool]:
        esq = self.nao()
        while self.kw("AND"):
            self.i += 1
            dir_ = self.nao()
            esq = (lambda a, b: lambda r: a(r) and b(r))(esq, dir_)
        return esq

    def nao(self) -> Callable[[Linha], bool]:
        if self.kw("NOT"):
            self.i += 1
            c = self.nao()
            return lambda r: not c(r)
        if self.op("("):
            self.i += 1
            c = self.condicao()
            self.exige_op(")")
            return c
        return self.predicado()

    def valor(self) -> Callable[[Linha], Any]:
        t = self.prox()
        if t is None:
            raise ErroSQL("valor esperado")
        self.i += 1
        if t.tipo == "NUM":
            v: Any = float(t.valor) if "." in t.valor else int(t.valor)
            return lambda r: v
        if t.tipo == "STR":
            s = t.valor[1:-1].replace("''", "'")
            return lambda r: s
        if t.tipo == "ID":
            u = t.valor.upper()
            if u == "NULL":
                return lambda r: None
            if u in ("TRUE", "FALSE"):
                b = u == "TRUE"
                return lambda r: b
            if u in _RESERVADAS:
                raise ErroSQL(f"palavra reservada inesperada: {t.valor}")
            nome = t.valor
            return lambda r: r.get(nome)
        raise ErroSQL(f"valor inesperado: {t.valor!r}")

    def predicado(self) -> Callable[[Linha], bool]:
        a = self.valor()
        if self.kw("IS"):
            self.i += 1
            neg = self.kw("NOT")
            if neg:
                self.i += 1
            self.exige_kw("NULL")
            return lambda r: (a(r) is None) != neg
        neg = False
        if self.kw("NOT"):
            self.i += 1
            neg = True
            if not self.kw("LIKE", "IN"):
                raise ErroSQL("esperado LIKE ou IN após NOT")
        if self.kw("LIKE"):
            self.i += 1
            b = self.valor()
            return lambda r: _like(a(r), b(r)) != neg
        if self.kw("IN"):
            self.i += 1
            self.exige_op("(")
            itens = [self.valor()]
            while self.op(","):
                self.i += 1
                itens.append(self.valor())
            self.exige_op(")")
            return lambda r: (a(r) in [i(r) for i in itens]) != neg
        t = self.prox()
        if t is None or t.tipo != "OP" or t.valor not in ("=", "!=", "<>", "<", "<=", ">", ">="):
            raise ErroSQL(f"operador de comparação esperado, encontrado {t.valor if t else 'fim'!r}")
        self.i += 1
        b = self.valor()
        return lambda r: _comparar(t.valor, a(r), b(r))


def _comparar(op: str, x: Any, y: Any) -> bool:
    if x is None or y is None:  # semântica SQL simplificada: NULL nunca satisfaz comparação
        return False
    try:
        return {"=": x == y, "!=": x != y, "<>": x != y, "<": x < y,
                "<=": x <= y, ">": x > y, ">=": x >= y}[op]
    except TypeError:
        raise ErroSQL(f"tipos incomparáveis: {type(x).__name__} e {type(y).__name__}") from None


def _like(x: Any, padrao: Any) -> bool:
    if not isinstance(x, str) or not isinstance(padrao, str):
        return False
    rx = "".join(".*" if c == "%" else "." if c == "_" else re.escape(c) for c in padrao)
    return re.fullmatch(rx, x, re.DOTALL | re.IGNORECASE) is not None


def consultar(sql: str, banco: Banco) -> list[Linha]:
    """Executa a consulta sobre `banco` (nome da tabela -> lista de dicts)."""
    p = _P(sql)
    p.exige_kw("SELECT")
    colunas: list[str] | None
    if p.op("*"):
        p.i += 1
        colunas = None
    else:
        colunas = [p.identificador()]
        while p.op(","):
            p.i += 1
            colunas.append(p.identificador())
    p.exige_kw("FROM")
    tabela = p.identificador()
    if tabela not in banco:
        raise ErroSQL(f"tabela inexistente: {tabela}")
    cond = None
    if p.kw("WHERE"):
        p.i += 1
        cond = p.condicao()
    ordem: tuple[str, bool] | None = None
    if p.kw("ORDER"):
        p.i += 1
        p.exige_kw("BY")
        col = p.identificador()
        desc = False
        if p.kw("ASC", "DESC"):
            desc = p.prox().valor.upper() == "DESC"  # type: ignore[union-attr]
            p.i += 1
        ordem = (col, desc)
    limite: int | None = None
    if p.kw("LIMIT"):
        p.i += 1
        t = p.prox()
        if t is None or t.tipo != "NUM" or "." in t.valor or int(t.valor) < 0:
            raise ErroSQL("LIMIT requer inteiro não negativo")
        limite = int(t.valor)
        p.i += 1
    if p.prox() is not None:
        raise ErroSQL(f"token inesperado: {p.prox().valor!r}")  # type: ignore[union-attr]

    linhas = [r for r in banco[tabela] if cond is None or cond(r)]
    if ordem:
        col, desc = ordem
        com = [r for r in linhas if r.get(col) is not None]
        sem = [r for r in linhas if r.get(col) is None]
        try:
            com.sort(key=lambda r: r[col], reverse=desc)
        except TypeError:
            raise ErroSQL(f"valores incomparáveis na coluna {col}") from None
        linhas = com + sem  # NULLs sempre por último
    if limite is not None:
        linhas = linhas[:limite]
    if colunas is None:
        return [dict(r) for r in linhas]
    return [{c: r.get(c) for c in colunas} for r in linhas]
