"""Tokenizer e parser recursivo-descendente de um SQL pequeno.

Comandos: CREATE TABLE, INSERT, SELECT (JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT),
UPDATE e DELETE. Expressões: OR/AND/NOT, comparações, IS [NOT] NULL, [NOT] IN,
[NOT] BETWEEN, [NOT] LIKE, + - * / %, funções e agregações.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional, Union


class ErroSQL(Exception):
    pass


# ---------------- tokens ----------------
PALAVRAS = {
    "CREATE", "TABLE", "INSERT", "INTO", "VALUES", "SELECT", "FROM", "WHERE", "UPDATE", "SET",
    "DELETE", "JOIN", "INNER", "ON", "GROUP", "BY", "HAVING", "ORDER", "ASC", "DESC", "LIMIT",
    "AND", "OR", "NOT", "NULL", "TRUE", "FALSE", "IS", "IN", "BETWEEN", "LIKE", "AS", "PRIMARY",
    "KEY", "DISTINCT",
}

_ER = re.compile(r"""
    (?P<espaco>\s+|--[^\n]*)
  | (?P<numero>\d+\.\d+|\d+)
  | (?P<texto>'(?:[^']|'')*')
  | (?P<ident>[A-Za-z_][A-Za-z_0-9]*)
  | (?P<op><=|>=|<>|!=|[=<>+\-*/%(),.;])
""", re.VERBOSE)


@dataclass(frozen=True)
class Token:
    tipo: str   # KW, IDENT, NUM, STR, OP, FIM
    valor: Any
    pos: int


def tokenizar(sql: str) -> list[Token]:
    saida: list[Token] = []
    i = 0
    while i < len(sql):
        m = _ER.match(sql, i)
        if not m:
            raise ErroSQL(f"caractere inesperado {sql[i]!r} na posição {i}")
        g = m.lastgroup
        t = m.group()
        if g == "numero":
            saida.append(Token("NUM", float(t) if "." in t else int(t), i))
        elif g == "texto":
            saida.append(Token("STR", t[1:-1].replace("''", "'"), i))
        elif g == "ident":
            if t.upper() in PALAVRAS:
                saida.append(Token("KW", t.upper(), i))
            else:
                saida.append(Token("IDENT", t, i))
        elif g == "op":
            saida.append(Token("OP", "<>" if t == "!=" else t, i))
        i = m.end()
    if sql.count("'") % 2:
        raise ErroSQL("literal de texto não terminado")
    saida.append(Token("FIM", None, len(sql)))
    return saida


# ---------------- AST ----------------
@dataclass(frozen=True)
class Literal:
    valor: Any


@dataclass(frozen=True)
class Coluna:
    nome: str
    tabela: Optional[str] = None


@dataclass(frozen=True)
class Binario:
    op: str
    esq: Any
    dir: Any


@dataclass(frozen=True)
class Unario:
    op: str   # NOT, -
    expr: Any


@dataclass(frozen=True)
class EhNulo:
    expr: Any
    negado: bool = False


@dataclass(frozen=True)
class EmLista:
    expr: Any
    itens: tuple
    negado: bool = False


@dataclass(frozen=True)
class Entre:
    expr: Any
    lo: Any
    hi: Any
    negado: bool = False


@dataclass(frozen=True)
class Chamada:
    nome: str            # em maiúsculas
    args: tuple
    estrela: bool = False


@dataclass
class ItemSelect:
    expr: Any            # None = '*'
    alias: Optional[str] = None


@dataclass
class Juncao:
    tabela: str
    alias: Optional[str]
    condicao: Any


@dataclass
class CriarTabela:
    nome: str
    colunas: list[tuple[str, str, bool]]  # (nome, tipo, chave_primaria)


@dataclass
class Inserir:
    tabela: str
    colunas: Optional[list[str]]
    linhas: list[list[Any]]


@dataclass
class Selecionar:
    itens: list[ItemSelect]
    tabela: str
    alias: Optional[str] = None
    juncoes: list[Juncao] = field(default_factory=list)
    where: Any = None
    group_by: list[Any] = field(default_factory=list)
    having: Any = None
    order_by: list[tuple[Any, bool]] = field(default_factory=list)  # (expr, desc)
    limite: Optional[int] = None
    distinto: bool = False


@dataclass
class Atualizar:
    tabela: str
    atribuicoes: list[tuple[str, Any]]
    where: Any = None


@dataclass
class Apagar:
    tabela: str
    where: Any = None


Comando = Union[CriarTabela, Inserir, Selecionar, Atualizar, Apagar]
AGREGADOS = {"COUNT", "SUM", "AVG", "MIN", "MAX"}
TIPOS = {"INT", "INTEGER", "TEXT", "REAL", "FLOAT", "BOOL", "BOOLEAN", "VARCHAR"}


# ---------------- parser ----------------
class Parser:
    def __init__(self, sql: str) -> None:
        self.t = tokenizar(sql)
        self.i = 0

    # utilidades
    @property
    def atual(self) -> Token:
        return self.t[self.i]

    def _erro(self, esperado: str) -> ErroSQL:
        a = self.atual
        achado = "fim da entrada" if a.tipo == "FIM" else repr(a.valor)
        return ErroSQL(f"esperado {esperado}, encontrado {achado} (posição {a.pos})")

    def _kw(self, *palavras: str) -> bool:
        return self.atual.tipo == "KW" and self.atual.valor in palavras

    def _op(self, *ops: str) -> bool:
        return self.atual.tipo == "OP" and self.atual.valor in ops

    def _consumir_kw(self, palavra: str) -> None:
        if not self._kw(palavra):
            raise self._erro(palavra)
        self.i += 1

    def _consumir_op(self, op: str) -> None:
        if not self._op(op):
            raise self._erro(repr(op))
        self.i += 1

    def _ident(self) -> str:
        if self.atual.tipo != "IDENT":
            raise self._erro("identificador")
        v = self.atual.valor
        self.i += 1
        return v

    def _talvez_kw(self, palavra: str) -> bool:
        if self._kw(palavra):
            self.i += 1
            return True
        return False

    # comandos
    def comando(self) -> Comando:
        if self._kw("CREATE"):
            c = self._criar()
        elif self._kw("INSERT"):
            c = self._inserir()
        elif self._kw("SELECT"):
            c = self._select()
        elif self._kw("UPDATE"):
            c = self._atualizar()
        elif self._kw("DELETE"):
            c = self._apagar()
        else:
            raise self._erro("CREATE, INSERT, SELECT, UPDATE ou DELETE")
        if self._op(";"):
            self.i += 1
        if self.atual.tipo != "FIM":
            raise self._erro("fim do comando")
        return c

    def _criar(self) -> CriarTabela:
        self._consumir_kw("CREATE")
        self._consumir_kw("TABLE")
        nome = self._ident()
        self._consumir_op("(")
        cols = []
        while True:
            cn = self._ident()
            if self.atual.tipo != "IDENT" or self.atual.valor.upper() not in TIPOS:
                raise self._erro("tipo de coluna")
            tipo = self.atual.valor.upper()
            self.i += 1
            if self._op("("):  # VARCHAR(20)
                self.i += 1
                if self.atual.tipo != "NUM":
                    raise self._erro("tamanho")
                self.i += 1
                self._consumir_op(")")
            pk = False
            if self._talvez_kw("PRIMARY"):
                self._consumir_kw("KEY")
                pk = True
            cols.append((cn, tipo, pk))
            if self._op(","):
                self.i += 1
                continue
            break
        self._consumir_op(")")
        if len({c[0].lower() for c in cols}) != len(cols):
            raise ErroSQL("colunas duplicadas")
        if sum(1 for c in cols if c[2]) > 1:
            raise ErroSQL("mais de uma chave primária")
        return CriarTabela(nome, cols)

    def _inserir(self) -> Inserir:
        self._consumir_kw("INSERT")
        self._consumir_kw("INTO")
        tabela = self._ident()
        colunas = None
        if self._op("("):
            self.i += 1
            colunas = [self._ident()]
            while self._op(","):
                self.i += 1
                colunas.append(self._ident())
            self._consumir_op(")")
        self._consumir_kw("VALUES")
        linhas = []
        while True:
            self._consumir_op("(")
            linha = [self._expr()]
            while self._op(","):
                self.i += 1
                linha.append(self._expr())
            self._consumir_op(")")
            if colunas is not None and len(linha) != len(colunas):
                raise ErroSQL("número de valores diferente do número de colunas")
            linhas.append(linha)
            if self._op(","):
                self.i += 1
                continue
            break
        if len({len(l) for l in linhas}) != 1:
            raise ErroSQL("linhas com tamanhos diferentes")
        return Inserir(tabela, colunas, linhas)

    def _apelido(self) -> Optional[str]:
        if self._talvez_kw("AS"):
            return self._ident()
        if self.atual.tipo == "IDENT":
            return self._ident()
        return None

    def _select(self) -> Selecionar:
        self._consumir_kw("SELECT")
        distinto = self._talvez_kw("DISTINCT")
        itens = []
        while True:
            if self._op("*"):
                self.i += 1
                itens.append(ItemSelect(None))
            else:
                e = self._expr()
                itens.append(ItemSelect(e, self._apelido()))
            if self._op(","):
                self.i += 1
                continue
            break
        self._consumir_kw("FROM")
        tabela = self._ident()
        alias = self._apelido()
        s = Selecionar(itens, tabela, alias, distinto=distinto)
        while self._kw("JOIN", "INNER"):
            if self._talvez_kw("INNER"):
                pass
            self._consumir_kw("JOIN")
            t2 = self._ident()
            a2 = self._apelido()
            self._consumir_kw("ON")
            s.juncoes.append(Juncao(t2, a2, self._expr()))
        if self._talvez_kw("WHERE"):
            s.where = self._expr()
        if self._talvez_kw("GROUP"):
            self._consumir_kw("BY")
            s.group_by.append(self._expr())
            while self._op(","):
                self.i += 1
                s.group_by.append(self._expr())
        if self._talvez_kw("HAVING"):
            s.having = self._expr()
        if self._talvez_kw("ORDER"):
            self._consumir_kw("BY")
            while True:
                e = self._expr()
                desc = False
                if self._talvez_kw("DESC"):
                    desc = True
                else:
                    self._talvez_kw("ASC")
                s.order_by.append((e, desc))
                if self._op(","):
                    self.i += 1
                    continue
                break
        if self._talvez_kw("LIMIT"):
            if self.atual.tipo != "NUM" or not isinstance(self.atual.valor, int):
                raise self._erro("inteiro")
            s.limite = self.atual.valor
            self.i += 1
        return s

    def _atualizar(self) -> Atualizar:
        self._consumir_kw("UPDATE")
        tabela = self._ident()
        self._consumir_kw("SET")
        atrib = []
        while True:
            c = self._ident()
            self._consumir_op("=")
            atrib.append((c, self._expr()))
            if self._op(","):
                self.i += 1
                continue
            break
        where = self._expr() if self._talvez_kw("WHERE") else None
        return Atualizar(tabela, atrib, where)

    def _apagar(self) -> Apagar:
        self._consumir_kw("DELETE")
        self._consumir_kw("FROM")
        tabela = self._ident()
        where = self._expr() if self._talvez_kw("WHERE") else None
        return Apagar(tabela, where)

    # expressões (precedência: OR < AND < NOT < comparação < + - < * / % < unário)
    def _expr(self) -> Any:
        e = self._and()
        while self._talvez_kw("OR"):
            e = Binario("OR", e, self._and())
        return e

    def _and(self) -> Any:
        e = self._not()
        while self._talvez_kw("AND"):
            e = Binario("AND", e, self._not())
        return e

    def _not(self) -> Any:
        if self._talvez_kw("NOT"):
            return Unario("NOT", self._not())
        return self._comparacao()

    def _comparacao(self) -> Any:
        e = self._soma()
        if self._op("=", "<>", "<", "<=", ">", ">="):
            op = self.atual.valor
            self.i += 1
            return Binario(op, e, self._soma())
        if self._talvez_kw("IS"):
            neg = self._talvez_kw("NOT")
            self._consumir_kw("NULL")
            return EhNulo(e, neg)
        neg = False
        if self._kw("NOT") and self.t[self.i + 1].tipo == "KW" and self.t[self.i + 1].valor in ("IN", "BETWEEN", "LIKE"):
            self.i += 1
            neg = True
        if self._talvez_kw("IN"):
            self._consumir_op("(")
            itens = [self._soma()]
            while self._op(","):
                self.i += 1
                itens.append(self._soma())
            self._consumir_op(")")
            return EmLista(e, tuple(itens), neg)
        if self._talvez_kw("BETWEEN"):
            lo = self._soma()
            self._consumir_kw("AND")
            return Entre(e, lo, self._soma(), neg)
        if self._talvez_kw("LIKE"):
            r = Binario("LIKE", e, self._soma())
            return Unario("NOT", r) if neg else r
        return e

    def _soma(self) -> Any:
        e = self._termo()
        while self._op("+", "-"):
            op = self.atual.valor
            self.i += 1
            e = Binario(op, e, self._termo())
        return e

    def _termo(self) -> Any:
        e = self._unario()
        while self._op("*", "/", "%"):
            op = self.atual.valor
            self.i += 1
            e = Binario(op, e, self._unario())
        return e

    def _unario(self) -> Any:
        if self._op("-"):
            self.i += 1
            e = self._unario()
            if isinstance(e, Literal) and isinstance(e.valor, (int, float)):
                return Literal(-e.valor)
            return Unario("-", e)
        return self._primario()

    def _primario(self) -> Any:
        a = self.atual
        if a.tipo in ("NUM", "STR"):
            self.i += 1
            return Literal(a.valor)
        if self._kw("NULL", "TRUE", "FALSE"):
            self.i += 1
            return Literal({"NULL": None, "TRUE": True, "FALSE": False}[a.valor])
        if self._op("("):
            self.i += 1
            e = self._expr()
            self._consumir_op(")")
            return e
        if a.tipo == "IDENT":
            nome = self._ident()
            if self._op("("):
                self.i += 1
                up = nome.upper()
                if self._op("*"):
                    if up != "COUNT":
                        raise ErroSQL("* só é permitido em COUNT")
                    self.i += 1
                    self._consumir_op(")")
                    return Chamada(up, (), True)
                args = []
                if not self._op(")"):
                    args.append(self._expr())
                    while self._op(","):
                        self.i += 1
                        args.append(self._expr())
                self._consumir_op(")")
                if up in AGREGADOS and len(args) != 1:
                    raise ErroSQL(f"{up} espera exatamente 1 argumento")
                return Chamada(up, tuple(args))
            if self._op("."):
                self.i += 1
                return Coluna(self._ident(), nome)
            return Coluna(nome)
        raise self._erro("expressão")


def parse(sql: str) -> Comando:
    return Parser(sql).comando()


def contem_agregado(expr: Any) -> bool:
    """True se a expressão contém COUNT/SUM/AVG/MIN/MAX."""
    if isinstance(expr, Chamada):
        return expr.nome in AGREGADOS or any(contem_agregado(a) for a in expr.args)
    if isinstance(expr, Binario):
        return contem_agregado(expr.esq) or contem_agregado(expr.dir)
    if isinstance(expr, (Unario, EhNulo)):
        return contem_agregado(expr.expr)
    if isinstance(expr, EmLista):
        return contem_agregado(expr.expr) or any(contem_agregado(i) for i in expr.itens)
    if isinstance(expr, Entre):
        return any(contem_agregado(x) for x in (expr.expr, expr.lo, expr.hi))
    return False
