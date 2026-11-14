"""Parser combinators monádicos sobre strings."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

Resultado = Optional[Tuple[Any, str]]


class ErroParse(Exception):
    pass


@dataclass(frozen=True)
class Parser:
    """run(texto) -> (valor, resto) ou None em caso de falha."""
    run: Callable[[str], Resultado]

    def parse(self, texto: str) -> Resultado:
        return self.run(texto)

    def map(self, f: Callable[[Any], Any]) -> "Parser":
        def run(s: str) -> Resultado:
            r = self.run(s)
            return None if r is None else (f(r[0]), r[1])
        return Parser(run)

    def bind(self, f: Callable[[Any], "Parser"]) -> "Parser":
        def run(s: str) -> Resultado:
            r = self.run(s)
            return None if r is None else f(r[0]).run(r[1])
        return Parser(run)

    def ap(self, outro: "Parser") -> "Parser":
        return self.bind(lambda f: outro.map(f))

    def __or__(self, outro: "Parser") -> "Parser":
        """Escolha à esquerda com retrocesso: tenta self e, se falhar, outro."""
        def run(s: str) -> Resultado:
            r = self.run(s)
            return r if r is not None else outro.run(s)
        return Parser(run)

    def __rshift__(self, outro: "Parser") -> "Parser":
        """Sequência descartando o resultado da esquerda."""
        return self.bind(lambda _: outro)

    def __lshift__(self, outro: "Parser") -> "Parser":
        """Sequência descartando o resultado da direita."""
        return self.bind(lambda a: outro.map(lambda _: a))


def unit(valor: Any) -> Parser:
    return Parser(lambda s: (valor, s))


def falha() -> Parser:
    return Parser(lambda s: None)


def item() -> Parser:
    return Parser(lambda s: (s[0], s[1:]) if s else None)


def sat(pred: Callable[[str], bool]) -> Parser:
    return item().bind(lambda c: unit(c) if pred(c) else falha())


def char(c: str) -> Parser:
    return sat(lambda x: x == c)


def string(prefixo: str) -> Parser:
    return Parser(lambda s: (prefixo, s[len(prefixo):]) if s.startswith(prefixo) else None)


def digito() -> Parser:
    return sat(lambda c: c in "0123456789")


def fim() -> Parser:
    return Parser(lambda s: (None, s) if not s else None)


def preguicoso(fabrica: Callable[[], Parser]) -> Parser:
    """Permite gramáticas recursivas adiando a construção do parser."""
    return Parser(lambda s: fabrica().run(s))


def many(p: Parser) -> Parser:
    def run(s: str) -> Resultado:
        valores: List[Any] = []
        while True:
            r = p.run(s)
            if r is None or r[1] == s:  # falhou ou não consumiu: evita laço infinito
                if r is not None:
                    valores.append(r[0])
                return valores, s
            valores.append(r[0])
            s = r[1]
    return Parser(run)


def many1(p: Parser) -> Parser:
    return p.bind(lambda x: many(p).map(lambda xs: [x] + xs))


def opcional(p: Parser, padrao: Any = None) -> Parser:
    return p | unit(padrao)


def sep_by1(p: Parser, sep: Parser) -> Parser:
    return p.bind(lambda x: many(sep >> p).map(lambda xs: [x] + xs))


def sep_by(p: Parser, sep: Parser) -> Parser:
    return sep_by1(p, sep) | unit([])


def entre(abre: Parser, p: Parser, fecha: Parser) -> Parser:
    return abre >> p << fecha


def chainl1(p: Parser, op: Parser) -> Parser:
    """Associatividade à esquerda: op devolve uma função binária."""
    def resto(a: Any) -> Parser:
        return op.bind(lambda f: p.bind(lambda b: resto(f(a, b)))) | unit(a)
    return p.bind(resto)


def espacos() -> Parser:
    return many(sat(str.isspace)).map(lambda _: None)


def token(p: Parser) -> Parser:
    return p << espacos()


def simbolo(s: str) -> Parser:
    return token(string(s))


def inteiro() -> Parser:
    sinal = opcional(char("-"), "")
    return sinal.bind(
        lambda sg: many1(digito()).map(lambda ds: int(sg + "".join(ds)))
    )


def numero() -> Parser:
    return token(inteiro())


def executar(p: Parser, texto: str) -> Any:
    """Exige que todo o texto seja consumido; levanta ErroParse caso contrário."""
    r = (espacos() >> p << fim()).run(texto)
    if r is None:
        raise ErroParse(f"falha ao analisar: {texto!r}")
    return r[0]


# Gramática de expressões aritméticas ----------------------------------------------

def _expressao() -> Parser:
    soma = simbolo("+").map(lambda _: lambda a, b: a + b) | simbolo("-").map(lambda _: lambda a, b: a - b)
    mult = simbolo("*").map(lambda _: lambda a, b: a * b) | simbolo("/").map(lambda _: _dividir)
    fator = numero() | entre(simbolo("("), preguicoso(_expressao), simbolo(")"))
    termo = chainl1(fator, mult)
    return chainl1(termo, soma)


def _dividir(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError("divisão por zero")
    return a // b


def calcular(texto: str) -> int:
    return executar(_expressao(), texto)


def lista_de_inteiros() -> Parser:
    return entre(simbolo("["), sep_by(numero(), simbolo(",")), simbolo("]"))
