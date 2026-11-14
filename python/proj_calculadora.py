"""Mini-calculadora: tokenizer + parser descendente recursivo com precedencia."""
import re
from typing import List


class ErroCalculo(Exception):
    pass


_TOKEN = re.compile(r"\s*(?:(\d+\.?\d*|\.\d+)|(\S))")


def tokenizar(texto: str) -> List[str]:
    tokens: List[str] = []
    for m in _TOKEN.finditer(texto):
        if m.group(1) is not None:
            tokens.append(m.group(1))
        else:
            if m.group(2) not in "+-*/^()":
                raise ErroCalculo(f"caractere invalido: {m.group(2)!r}")
            tokens.append(m.group(2))
    return tokens


class _Parser:
    def __init__(self, tokens: List[str]) -> None:
        self.t = tokens
        self.i = 0

    def _peek(self) -> str:
        return self.t[self.i] if self.i < len(self.t) else ""

    def _next(self) -> str:
        tok = self._peek()
        self.i += 1
        return tok

    def expressao(self) -> float:
        v = self.termo()
        while self._peek() in ("+", "-"):
            v = v + self.termo() if self._next() == "+" else v - self.termo()
        return v

    def termo(self) -> float:
        v = self.potencia()
        while self._peek() in ("*", "/"):
            if self._next() == "*":
                v *= self.potencia()
            else:
                d = self.potencia()
                if d == 0:
                    raise ErroCalculo("divisao por zero")
                v /= d
        return v

    def potencia(self) -> float:
        base = self.unario()
        if self._peek() == "^":
            self._next()
            return base ** self.potencia()  # associativa a direita
        return base

    def unario(self) -> float:
        if self._peek() == "-":
            self._next()
            return -self.unario()
        if self._peek() == "+":
            self._next()
            return self.unario()
        return self.atomo()

    def atomo(self) -> float:
        tok = self._next()
        if tok == "(":
            v = self.expressao()
            if self._next() != ")":
                raise ErroCalculo("parenteses nao balanceados")
            return v
        try:
            return float(tok)
        except ValueError:
            raise ErroCalculo("expressao invalida") from None


def avaliar(texto: str) -> float:
    p = _Parser(tokenizar(texto))
    valor = p.expressao()
    if p.i != len(p.t):
        raise ErroCalculo("tokens sobrando")
    return valor
