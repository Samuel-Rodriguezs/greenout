"""Mini-Lisp: leitor de S-expressions e avaliador com closures."""
from __future__ import annotations

import math
import operator
from typing import Any


class ErroLisp(Exception):
    """Erro de leitura ou avaliação."""


class Simbolo(str):
    """Símbolo Lisp (distinto de string literal)."""


def tokenizar(texto: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(texto):
        c = texto[i]
        if c.isspace():
            i += 1
        elif c == ";":
            while i < len(texto) and texto[i] != "\n":
                i += 1
        elif c in "()'":
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while j < len(texto) and texto[j] != '"':
                j += 2 if texto[j] == "\\" else 1
            if j >= len(texto):
                raise ErroLisp("string não terminada")
            tokens.append(texto[i:j + 1])
            i = j + 1
        else:
            j = i
            while j < len(texto) and not texto[j].isspace() and texto[j] not in "()';":
                j += 1
            tokens.append(texto[i:j])
            i = j
    return tokens


def _atomo(tok: str) -> Any:
    if tok.startswith('"'):
        return tok[1:-1].replace('\\"', '"').replace("\\n", "\n")
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(tok)
    except ValueError:
        return Simbolo(tok)


def _ler(tokens: list[str], pos: int) -> tuple[Any, int]:
    if pos >= len(tokens):
        raise ErroLisp("fim inesperado da entrada")
    tok = tokens[pos]
    if tok == "(":
        lista: list[Any] = []
        pos += 1
        while True:
            if pos >= len(tokens):
                raise ErroLisp("parêntese '(' não fechado")
            if tokens[pos] == ")":
                return lista, pos + 1
            item, pos = _ler(tokens, pos)
            lista.append(item)
    if tok == ")":
        raise ErroLisp("')' inesperado")
    if tok == "'":
        item, pos = _ler(tokens, pos + 1)
        return [Simbolo("quote"), item], pos
    return _atomo(tok), pos + 1


def ler(texto: str) -> list[Any]:
    """Lê todas as expressões do texto."""
    tokens = tokenizar(texto)
    exprs: list[Any] = []
    pos = 0
    while pos < len(tokens):
        e, pos = _ler(tokens, pos)
        exprs.append(e)
    return exprs


class Ambiente(dict):
    def __init__(self, externo: "Ambiente | None" = None, **kw: Any) -> None:
        super().__init__(**kw)
        self.externo = externo

    def achar(self, nome: str) -> "Ambiente":
        a: Ambiente | None = self
        while a is not None:
            if nome in a:
                return a
            a = a.externo
        raise ErroLisp(f"símbolo indefinido: {nome}")


class Lambda:
    def __init__(self, params: list[Any], corpo: Any, env: Ambiente) -> None:
        self.params, self.corpo, self.env = params, corpo, env

    def __call__(self, *args: Any) -> Any:
        return avaliar(self.corpo, self.novo_ambiente(args))

    def novo_ambiente(self, args: Any) -> Ambiente:
        if len(args) != len(self.params):
            raise ErroLisp(f"esperava {len(self.params)} argumentos, recebeu {len(args)}")
        return Ambiente(self.env, **dict(zip(self.params, args)))


def _div(a: Any, b: Any) -> Any:
    if b == 0:
        raise ErroLisp("divisão por zero")
    return a // b if isinstance(a, int) and isinstance(b, int) and a % b == 0 else a / b


def ambiente_padrao() -> Ambiente:
    env = Ambiente()
    env.update({
        "+": lambda *a: sum(a), "-": lambda a, *b: -a if not b else a - sum(b),
        "*": lambda *a: math.prod(a), "/": _div,
        "<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge,
        "=": operator.eq, "mod": operator.mod, "abs": abs,
        "car": lambda l: l[0], "cdr": lambda l: l[1:],
        "cons": lambda x, l: [x] + list(l), "list": lambda *a: list(a),
        "length": len, "null?": lambda l: l == [], "not": operator.not_,
        "list?": lambda x: isinstance(x, list),
        "append": lambda *ls: [x for l in ls for x in l],
        "map": lambda f, l: [f(x) for x in l],
        "filter": lambda f, l: [x for x in l if f(x)],
    })
    return env


def avaliar(x: Any, env: Ambiente) -> Any:
    while True:
        if isinstance(x, Simbolo):
            return env.achar(x)[x]
        if not isinstance(x, list):
            return x
        if not x:
            return []
        op = x[0]
        if op == "quote":
            return x[1]
        if op == "if":
            if len(x) != 4:
                raise ErroLisp("if requer 3 argumentos")
            cond = avaliar(x[1], env)
            x = x[2] if (cond is not False and cond != []) else x[3]
            continue
        if op == "define":
            if isinstance(x[1], list):  # (define (f a b) corpo)
                env[x[1][0]] = Lambda(x[1][1:], x[2], env)
            else:
                env[x[1]] = avaliar(x[2], env)
            return None
        if op == "set!":
            env.achar(x[1])[x[1]] = avaliar(x[2], env)
            return None
        if op == "lambda":
            return Lambda(x[1], x[2], env)
        if op == "begin":
            for e in x[1:-1]:
                avaliar(e, env)
            x = x[-1]
            continue
        if op == "let":
            novo = Ambiente(env)
            for nome, val in x[1]:
                novo[nome] = avaliar(val, env)
            env, x = novo, x[2]
            continue
        f = avaliar(op, env)
        args = [avaliar(a, env) for a in x[1:]]
        if isinstance(f, Lambda):
            env, x = f.novo_ambiente(args), f.corpo
            continue
        if not callable(f):
            raise ErroLisp(f"não é função: {f!r}")
        return f(*args)


def executar(texto: str, env: Ambiente | None = None) -> Any:
    """Avalia todas as expressões e devolve o valor da última."""
    env = env if env is not None else ambiente_padrao()
    resultado = None
    for e in ler(texto):
        resultado = avaliar(e, env)
    return resultado
