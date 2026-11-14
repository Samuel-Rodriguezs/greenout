"""Tokenizer genérico baseado em regras (regex nomeadas) com posição linha/coluna."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator


class ErroLexico(Exception):
    """Caractere que não casa com nenhuma regra."""


@dataclass(frozen=True)
class Token:
    tipo: str
    valor: str
    linha: int
    coluna: int


class Tokenizador:
    """Cria um tokenizador a partir de uma lista de (tipo, padrão).

    Regras cujo tipo está em `ignorar` são descartadas (ex.: espaços).
    A primeira regra que casar vence.
    """

    def __init__(self, regras: list[tuple[str, str]], ignorar: tuple[str, ...] = ("ESPACO",)) -> None:
        if not regras:
            raise ValueError("é preciso ao menos uma regra")
        self.ignorar = set(ignorar)
        self._re = re.compile("|".join(f"(?P<{t}>{p})" for t, p in regras))

    def tokenizar(self, texto: str) -> Iterator[Token]:
        pos, linha, inicio_linha = 0, 1, 0
        while pos < len(texto):
            m = self._re.match(texto, pos)
            if m is None or m.end() == pos:
                raise ErroLexico(
                    f"caractere inesperado {texto[pos]!r} na linha {linha}, coluna {pos - inicio_linha + 1}"
                )
            tipo = m.lastgroup or ""
            valor = m.group()
            if tipo not in self.ignorar:
                yield Token(tipo, valor, linha, pos - inicio_linha + 1)
            quebras = valor.count("\n")
            if quebras:
                linha += quebras
                inicio_linha = pos + valor.rindex("\n") + 1
            pos = m.end()

    def lista(self, texto: str) -> list[Token]:
        return list(self.tokenizar(texto))


def tokenizador_aritmetico() -> Tokenizador:
    """Tokenizador pronto para expressões aritméticas com identificadores."""
    return Tokenizador([
        ("NUMERO", r"\d+(?:\.\d+)?"),
        ("ID", r"[A-Za-z_]\w*"),
        ("OP", r"[-+*/^=]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("VIRGULA", r","),
        ("ESPACO", r"\s+"),
    ])
