"""Motor de regex por backtracking: literais, ., *, +, ?, classes [a-z] / [^...], ^, $, | e grupos ( )."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator


class ErroRegex(Exception):
    """Padrão inválido."""


# AST: ("lit", c) ("any",) ("cls", conjunto_de_faixas, negado) ("cat", [nós]) ("alt", [nós])
# ("rep", nó, min, max) ("bol",) ("eol",)
No = tuple


class _Parser:
    def __init__(self, padrao: str) -> None:
        self.p = padrao
        self.i = 0

    def alternativa(self) -> No:
        opcoes = [self.sequencia()]
        while self.i < len(self.p) and self.p[self.i] == "|":
            self.i += 1
            opcoes.append(self.sequencia())
        return opcoes[0] if len(opcoes) == 1 else ("alt", opcoes)

    def sequencia(self) -> No:
        itens: list[No] = []
        while self.i < len(self.p) and self.p[self.i] not in "|)":
            itens.append(self.quantificado())
        return ("cat", itens)

    def quantificado(self) -> No:
        no = self.atomo()
        while self.i < len(self.p) and self.p[self.i] in "*+?":
            q = self.p[self.i]
            self.i += 1
            no = ("rep", no, 1 if q == "+" else 0, 1 if q == "?" else None)
        return no

    def atomo(self) -> No:
        c = self.p[self.i]
        self.i += 1
        if c in "*+?":
            raise ErroRegex(f"quantificador {c!r} sem operando")
        if c == "(":
            no = self.alternativa()
            if self.i >= len(self.p) or self.p[self.i] != ")":
                raise ErroRegex("parêntese '(' não fechado")
            self.i += 1
            return no
        if c == ".":
            return ("any",)
        if c == "^":
            return ("bol",)
        if c == "$":
            return ("eol",)
        if c == "[":
            return self.classe()
        if c == "\\":
            if self.i >= len(self.p):
                raise ErroRegex("barra invertida no final")
            e = self.p[self.i]
            self.i += 1
            if e == "d":
                return ("cls", [("0", "9")], False)
            if e == "w":
                return ("cls", [("a", "z"), ("A", "Z"), ("0", "9"), ("_", "_")], False)
            if e == "s":
                return ("cls", [(" ", " "), ("\t", "\t"), ("\n", "\n"), ("\r", "\r")], False)
            return ("lit", {"n": "\n", "t": "\t"}.get(e, e))
        return ("lit", c)

    def classe(self) -> No:
        negado = self.i < len(self.p) and self.p[self.i] == "^"
        if negado:
            self.i += 1
        faixas: list[tuple[str, str]] = []
        primeiro = True
        while True:
            if self.i >= len(self.p):
                raise ErroRegex("classe '[' não fechada")
            c = self.p[self.i]
            if c == "]" and not primeiro:
                self.i += 1
                return ("cls", faixas, negado)
            primeiro = False
            if c == "\\" and self.i + 1 < len(self.p):
                self.i += 1
                c = self.p[self.i]
            self.i += 1
            if self.i + 1 < len(self.p) and self.p[self.i] == "-" and self.p[self.i + 1] != "]":
                fim = self.p[self.i + 1]
                if fim < c:
                    raise ErroRegex(f"faixa inválida {c}-{fim}")
                faixas.append((c, fim))
                self.i += 2
            else:
                faixas.append((c, c))


def _compilar(padrao: str) -> No:
    p = _Parser(padrao)
    no = p.alternativa()
    if p.i != len(padrao):
        raise ErroRegex("parêntese ')' inesperado")
    return no


Continuacao = Callable[[int], Iterator[int]]


def _casar(no: No, s: str, i: int, k: Continuacao) -> Iterator[int]:
    """Gerador de posições finais; k é a continuação (backtracking via geradores)."""
    tipo = no[0]
    if tipo == "lit":
        if i < len(s) and s[i] == no[1]:
            yield from k(i + 1)
    elif tipo == "any":
        if i < len(s) and s[i] != "\n":
            yield from k(i + 1)
    elif tipo == "cls":
        if i < len(s):
            dentro = any(a <= s[i] <= b for a, b in no[1])
            if dentro != no[2]:
                yield from k(i + 1)
    elif tipo == "bol":
        if i == 0:
            yield from k(i)
    elif tipo == "eol":
        if i == len(s):
            yield from k(i)
    elif tipo == "cat":
        yield from _cat(no[1], 0, s, i, k)
    elif tipo == "alt":
        for op in no[1]:
            yield from _casar(op, s, i, k)
    elif tipo == "rep":
        yield from _rep(no[1], no[2], no[3], 0, s, i, k)


def _cat(itens: list[No], idx: int, s: str, i: int, k: Continuacao) -> Iterator[int]:
    if idx == len(itens):
        yield from k(i)
        return
    yield from _casar(itens[idx], s, i, lambda j: _cat(itens, idx + 1, s, j, k))


def _rep(no: No, minimo: int, maximo: int | None, feitos: int, s: str, i: int,
         k: Continuacao) -> Iterator[int]:
    # guloso: tenta mais uma repetição antes de parar
    if maximo is None or feitos < maximo:
        def depois(j: int) -> Iterator[int]:
            if j == i and feitos >= minimo:  # evita laço infinito com repetição vazia
                return iter(())
            return _rep(no, minimo, maximo, feitos + 1, s, j, k)
        yield from _casar(no, s, i, depois)
    if feitos >= minimo:
        yield from k(i)


@dataclass(frozen=True)
class Casamento:
    inicio: int
    fim: int
    texto: str


class Regex:
    def __init__(self, padrao: str) -> None:
        self.padrao = padrao
        self._ast = _compilar(padrao)

    def casa_em(self, s: str, i: int) -> Casamento | None:
        for fim in _casar(self._ast, s, i, lambda j: iter((j,))):
            return Casamento(i, fim, s[i:fim])
        return None

    def match(self, s: str) -> Casamento | None:
        """Casa a partir do início da string."""
        return self.casa_em(s, 0)

    def fullmatch(self, s: str) -> bool:
        return any(True for _ in _casar(self._ast, s, 0, lambda j: iter((j,)) if j == len(s) else iter(())))

    def search(self, s: str) -> Casamento | None:
        for i in range(len(s) + 1):
            m = self.casa_em(s, i)
            if m:
                return m
        return None

    def findall(self, s: str) -> list[str]:
        achados: list[str] = []
        i = 0
        while i <= len(s):
            m = self.casa_em(s, i)
            if m is None:
                i += 1
            else:
                achados.append(m.texto)
                i = m.fim if m.fim > i else i + 1
        return achados


def compilar(padrao: str) -> Regex:
    return Regex(padrao)
