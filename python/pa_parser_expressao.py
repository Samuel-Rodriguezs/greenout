"""Parser recursivo descendente de expressões aritméticas (+ - * / ** parênteses, unário)."""
import re
from typing import List

_TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|(\*\*|[-+*/()]))")


class ErroSintaxe(ValueError):
    pass


def _tokenizar(texto: str) -> List[str]:
    tokens: List[str] = []
    pos = 0
    texto = texto.rstrip()
    while pos < len(texto):
        m = _TOKEN.match(texto, pos)
        if not m:
            raise ErroSintaxe(f"caractere inesperado na posição {pos}")
        tokens.append(m.group(1) or m.group(2))
        pos = m.end()
    return tokens


class _Parser:
    def __init__(self, tokens: List[str]) -> None:
        self.t = tokens
        self.i = 0

    def espiar(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def consumir(self) -> str:
        tok = self.espiar()
        if tok is None:
            raise ErroSintaxe("fim inesperado")
        self.i += 1
        return tok

    def expressao(self) -> float:
        v = self.termo()
        while self.espiar() in ("+", "-"):
            if self.consumir() == "+":
                v += self.termo()
            else:
                v -= self.termo()
        return v

    def termo(self) -> float:
        v = self.unario()
        while self.espiar() in ("*", "/"):
            if self.consumir() == "*":
                v *= self.unario()
            else:
                d = self.unario()
                if d == 0:
                    raise ZeroDivisionError("divisão por zero")
                v /= d
        return v

    def unario(self) -> float:
        if self.espiar() == "-":
            self.consumir()
            return -self.unario()
        if self.espiar() == "+":
            self.consumir()
            return self.unario()
        return self.potencia()

    def potencia(self) -> float:
        base = self.primario()
        if self.espiar() == "**":
            self.consumir()
            return base ** self.unario()  # associativa à direita
        return base

    def primario(self) -> float:
        tok = self.consumir()
        if tok == "(":
            v = self.expressao()
            if self.espiar() != ")":
                raise ErroSintaxe("parêntese não fechado")
            self.consumir()
            return v
        try:
            return float(tok)
        except ValueError:
            raise ErroSintaxe(f"token inesperado: {tok}") from None


def calcular(texto: str) -> float:
    p = _Parser(_tokenizar(texto))
    valor = p.expressao()
    if p.espiar() is not None:
        raise ErroSintaxe(f"token inesperado: {p.espiar()}")
    return valor
