"""Calculadora com variáveis, funções nativas e funções definidas pelo usuário.

Exemplos: `x = 2 + 3`, `f(a, b) = a * b + x`, `f(2, 3)`, `2 ^ 3 ^ 2`, `sqrt(16)`.
"""
from __future__ import annotations

import math
from typing import Any, Callable

from lang_tokenizer import ErroLexico, Token, Tokenizador


class ErroCalculadora(Exception):
    """Erro de sintaxe ou avaliação."""


_TOK = Tokenizador([
    ("NUMERO", r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"),
    ("ID", r"[A-Za-z_]\w*"),
    ("OP", r"[-+*/^%=(),]"),
    ("ESPACO", r"\s+"),
])

_NATIVAS: dict[str, Callable[..., float]] = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "exp": math.exp, "abs": abs, "floor": math.floor,
    "ceil": math.ceil, "min": min, "max": max, "round": round,
}
_CONSTANTES = {"pi": math.pi, "e": math.e}


class _Parser:
    def __init__(self, tokens: list[Token], calc: "Calculadora", locais: dict[str, float] | None = None) -> None:
        self.t, self.i, self.calc, self.locais = tokens, 0, calc, locais or {}

    def prox(self) -> Token | None:
        return self.t[self.i] if self.i < len(self.t) else None

    def eh(self, v: str) -> bool:
        t = self.prox()
        return t is not None and t.tipo == "OP" and t.valor == v

    def consome(self, v: str) -> None:
        if not self.eh(v):
            t = self.prox()
            raise ErroCalculadora(f"esperado {v!r}, encontrado {t.valor if t else 'fim'!r}")
        self.i += 1

    def expressao(self) -> float:
        v = self.termo()
        while self.eh("+") or self.eh("-"):
            op = self.t[self.i].valor
            self.i += 1
            d = self.termo()
            v = v + d if op == "+" else v - d
        return v

    def termo(self) -> float:
        v = self.unario()
        while self.eh("*") or self.eh("/") or self.eh("%"):
            op = self.t[self.i].valor
            self.i += 1
            d = self.unario()
            if op == "*":
                v *= d
            else:
                if d == 0:
                    raise ErroCalculadora("divisão por zero")
                v = v / d if op == "/" else v % d
        return v

    def unario(self) -> float:
        if self.eh("-"):
            self.i += 1
            return -self.unario()
        if self.eh("+"):
            self.i += 1
            return self.unario()
        return self.potencia()

    def potencia(self) -> float:
        base = self.primario()
        if self.eh("^"):
            self.i += 1
            exp = self.unario()  # associativa à direita
            try:
                r = base ** exp
            except (ZeroDivisionError, OverflowError) as e:
                raise ErroCalculadora(f"erro na potência: {e}") from None
            if isinstance(r, complex):
                raise ErroCalculadora("resultado complexo")
            return r
        return base

    def primario(self) -> float:
        t = self.prox()
        if t is None:
            raise ErroCalculadora("expressão incompleta")
        self.i += 1
        if t.tipo == "NUMERO":
            return float(t.valor)
        if t.tipo == "ID":
            if self.eh("("):
                self.i += 1
                args: list[float] = []
                if not self.eh(")"):
                    args.append(self.expressao())
                    while self.eh(","):
                        self.i += 1
                        args.append(self.expressao())
                self.consome(")")
                return self.calc.chamar(t.valor, args)
            if t.valor in self.locais:
                return self.locais[t.valor]
            if t.valor in self.calc.variaveis:
                return self.calc.variaveis[t.valor]
            if t.valor in _CONSTANTES:
                return _CONSTANTES[t.valor]
            raise ErroCalculadora(f"variável indefinida: {t.valor}")
        if t.tipo == "OP" and t.valor == "(":
            v = self.expressao()
            self.consome(")")
            return v
        raise ErroCalculadora(f"token inesperado: {t.valor!r}")


class Calculadora:
    def __init__(self) -> None:
        self.variaveis: dict[str, float] = {}
        self.funcoes: dict[str, tuple[list[str], list[Token]]] = {}
        self._profundidade = 0

    def chamar(self, nome: str, args: list[float]) -> float:
        if nome in self.funcoes:
            params, corpo = self.funcoes[nome]
            if len(args) != len(params):
                raise ErroCalculadora(f"{nome} espera {len(params)} argumentos, recebeu {len(args)}")
            if self._profundidade > 100:
                raise ErroCalculadora("recursão profunda demais")
            self._profundidade += 1
            try:
                p = _Parser(corpo, self, dict(zip(params, args)))
                v = p.expressao()
                if p.prox() is not None:
                    raise ErroCalculadora(f"token inesperado: {p.prox().valor!r}")  # type: ignore[union-attr]
                return v
            finally:
                self._profundidade -= 1
        if nome in _NATIVAS:
            try:
                return float(_NATIVAS[nome](*args))
            except (ValueError, TypeError, OverflowError) as e:
                raise ErroCalculadora(f"erro em {nome}: {e}") from None
        raise ErroCalculadora(f"função indefinida: {nome}")

    def avaliar(self, linha: str) -> float | None:
        """Avalia uma linha. Atribuições de variável devolvem o valor; definições de função, None."""
        try:
            tokens = list(_TOK.tokenizar(linha))
        except ErroLexico as e:
            raise ErroCalculadora(str(e)) from None
        if not tokens:
            raise ErroCalculadora("linha vazia")
        ops = [t.valor for t in tokens if t.tipo == "OP"]
        if "=" in ops:
            return self._atribuicao(tokens)
        p = _Parser(tokens, self)
        v = p.expressao()
        if p.prox() is not None:
            raise ErroCalculadora(f"token inesperado: {p.prox().valor!r}")  # type: ignore[union-attr]
        return v

    def _atribuicao(self, tokens: list[Token]) -> float | None:
        idx = next(i for i, t in enumerate(tokens) if t.tipo == "OP" and t.valor == "=")
        esq, dir_ = tokens[:idx], tokens[idx + 1:]
        if not dir_:
            raise ErroCalculadora("lado direito vazio")
        if len(esq) == 1 and esq[0].tipo == "ID":
            if esq[0].valor in _CONSTANTES:
                raise ErroCalculadora(f"não é possível redefinir {esq[0].valor}")
            p = _Parser(dir_, self)
            v = p.expressao()
            if p.prox() is not None:
                raise ErroCalculadora(f"token inesperado: {p.prox().valor!r}")
            self.variaveis[esq[0].valor] = v
            return v
        # definição de função: nome ( ID , ID ... ) = corpo
        if len(esq) >= 3 and esq[0].tipo == "ID" and esq[1].valor == "(" and esq[-1].valor == ")":
            nomes = esq[2:-1]
            params: list[str] = []
            for k, t in enumerate(nomes):
                if k % 2 == 0 and t.tipo == "ID":
                    params.append(t.valor)
                elif k % 2 == 1 and t.valor == ",":
                    continue
                else:
                    raise ErroCalculadora("lista de parâmetros inválida")
            if nomes and len(nomes) % 2 == 0:
                raise ErroCalculadora("lista de parâmetros inválida")
            if len(set(params)) != len(params):
                raise ErroCalculadora("parâmetros duplicados")
            self.funcoes[esq[0].valor] = (params, dir_)
            return None
        raise ErroCalculadora("lado esquerdo da atribuição inválido")


def calcular(linha: str) -> Any:
    """Atalho: avalia uma expressão numa calculadora nova."""
    return Calculadora().avaliar(linha)
