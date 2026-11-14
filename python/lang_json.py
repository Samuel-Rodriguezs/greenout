"""Parser de JSON próprio (descida recursiva), sem usar o módulo json."""
from __future__ import annotations

from typing import Any


class ErroJSON(Exception):
    """Erro de sintaxe JSON, com posição."""


_ESCAPES = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
_PROFUNDIDADE_MAX = 200


class _Parser:
    def __init__(self, s: str) -> None:
        self.s = s
        self.i = 0

    def erro(self, msg: str) -> ErroJSON:
        return ErroJSON(f"{msg} na posição {self.i}")

    def espaco(self) -> None:
        while self.i < len(self.s) and self.s[self.i] in " \t\n\r":
            self.i += 1

    def valor(self, prof: int = 0) -> Any:
        if prof > _PROFUNDIDADE_MAX:
            raise self.erro("aninhamento profundo demais")
        self.espaco()
        if self.i >= len(self.s):
            raise self.erro("fim inesperado")
        c = self.s[self.i]
        if c == "{":
            return self.objeto(prof)
        if c == "[":
            return self.lista(prof)
        if c == '"':
            return self.string()
        for lit, val in (("true", True), ("false", False), ("null", None)):
            if self.s.startswith(lit, self.i):
                self.i += len(lit)
                return val
        if c == "-" or c.isdigit():
            return self.numero()
        raise self.erro(f"caractere inesperado {c!r}")

    def numero(self) -> int | float:
        ini = self.i
        if self.s[self.i] == "-":
            self.i += 1
        if self.i < len(self.s) and self.s[self.i] == "0":
            self.i += 1
        else:
            self._digitos()
        flutuante = False
        if self.i < len(self.s) and self.s[self.i] == ".":
            flutuante = True
            self.i += 1
            self._digitos()
        if self.i < len(self.s) and self.s[self.i] in "eE":
            flutuante = True
            self.i += 1
            if self.i < len(self.s) and self.s[self.i] in "+-":
                self.i += 1
            self._digitos()
        txt = self.s[ini:self.i]
        return float(txt) if flutuante else int(txt)

    def _digitos(self) -> None:
        ini = self.i
        while self.i < len(self.s) and self.s[self.i].isdigit():
            self.i += 1
        if ini == self.i:
            raise self.erro("dígito esperado")

    def string(self) -> str:
        self.i += 1
        partes: list[str] = []
        while True:
            if self.i >= len(self.s):
                raise self.erro("string não terminada")
            c = self.s[self.i]
            if c == '"':
                self.i += 1
                return "".join(partes)
            if c < " ":
                raise self.erro("caractere de controle em string")
            if c == "\\":
                self.i += 1
                if self.i >= len(self.s):
                    raise self.erro("escape incompleto")
                e = self.s[self.i]
                if e == "u":
                    hexa = self.s[self.i + 1:self.i + 5]
                    if len(hexa) != 4 or any(h not in "0123456789abcdefABCDEF" for h in hexa):
                        raise self.erro("escape \\u inválido")
                    cod = int(hexa, 16)
                    self.i += 4
                    # par substituto
                    if 0xD800 <= cod < 0xDC00 and self.s.startswith("\\u", self.i + 1):
                        baixo = self.s[self.i + 3:self.i + 7]
                        try:
                            b = int(baixo, 16)
                        except ValueError:
                            raise self.erro("escape \\u inválido") from None
                        if 0xDC00 <= b < 0xE000:
                            cod = 0x10000 + ((cod - 0xD800) << 10) + (b - 0xDC00)
                            self.i += 6
                    partes.append(chr(cod))
                elif e in _ESCAPES:
                    partes.append(_ESCAPES[e])
                else:
                    raise self.erro(f"escape inválido \\{e}")
                self.i += 1
            else:
                partes.append(c)
                self.i += 1

    def lista(self, prof: int) -> list[Any]:
        self.i += 1
        itens: list[Any] = []
        self.espaco()
        if self.i < len(self.s) and self.s[self.i] == "]":
            self.i += 1
            return itens
        while True:
            itens.append(self.valor(prof + 1))
            self.espaco()
            if self.i >= len(self.s):
                raise self.erro("']' esperado")
            c = self.s[self.i]
            self.i += 1
            if c == "]":
                return itens
            if c != ",":
                self.i -= 1
                raise self.erro("',' ou ']' esperado")

    def objeto(self, prof: int) -> dict[str, Any]:
        self.i += 1
        obj: dict[str, Any] = {}
        self.espaco()
        if self.i < len(self.s) and self.s[self.i] == "}":
            self.i += 1
            return obj
        while True:
            self.espaco()
            if self.i >= len(self.s) or self.s[self.i] != '"':
                raise self.erro("chave string esperada")
            chave = self.string()
            self.espaco()
            if self.i >= len(self.s) or self.s[self.i] != ":":
                raise self.erro("':' esperado")
            self.i += 1
            obj[chave] = self.valor(prof + 1)
            self.espaco()
            if self.i >= len(self.s):
                raise self.erro("'}' esperado")
            c = self.s[self.i]
            self.i += 1
            if c == "}":
                return obj
            if c != ",":
                self.i -= 1
                raise self.erro("',' ou '}' esperado")


def carregar(texto: str) -> Any:
    """Converte texto JSON em objetos Python."""
    p = _Parser(texto)
    v = p.valor()
    p.espaco()
    if p.i != len(texto):
        raise p.erro("conteúdo extra após o valor")
    return v


def _escapar(s: str) -> str:
    saida = ['"']
    for c in s:
        if c == '"':
            saida.append('\\"')
        elif c == "\\":
            saida.append("\\\\")
        elif c == "\n":
            saida.append("\\n")
        elif c == "\r":
            saida.append("\\r")
        elif c == "\t":
            saida.append("\\t")
        elif c < " ":
            saida.append(f"\\u{ord(c):04x}")
        else:
            saida.append(c)
    saida.append('"')
    return "".join(saida)


def serializar(v: Any) -> str:
    """Converte objetos Python em texto JSON compacto."""
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return _escapar(v)
    if isinstance(v, (list, tuple)):
        return "[" + ",".join(serializar(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ",".join(f"{_escapar(str(k))}:{serializar(x)}" for k, x in v.items()) + "}"
    raise TypeError(f"tipo não serializável: {type(v).__name__}")
