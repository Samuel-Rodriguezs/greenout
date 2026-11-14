"""Lexer da linguagem Mini (primeira etapa do pipeline de compilação).

Gramática completa de Mini em EBNF (o parser em comp_parser implementa esta
especificação)::

    programa    = { funcao | comando } ;
    funcao      = "func" ID "(" [ param { "," param } ] ")" [ "->" tipo ] bloco ;
    param       = ID ":" tipo ;
    tipo        = "int" | "bool" | "void" ;
    bloco       = "{" { comando } "}" ;
    comando     = decl | atribuicao | se | enquanto | retorno
                | impressao | bloco | expr ";" ;
    decl        = "var" ID [ ":" tipo ] "=" expr ";" ;
    atribuicao  = ID "=" expr ";" ;
    se          = "if" "(" expr ")" bloco [ "else" ( se | bloco ) ] ;
    enquanto    = "while" "(" expr ")" bloco ;
    retorno     = "return" [ expr ] ";" ;
    impressao   = "print" "(" expr ")" ";" ;
    expr        = ou ;
    ou          = e { "||" e } ;
    e           = igualdade { "&&" igualdade } ;
    igualdade   = relacional { ( "==" | "!=" ) relacional } ;
    relacional  = soma { ( "<" | "<=" | ">" | ">=" ) soma } ;
    soma        = termo { ( "+" | "-" ) termo } ;
    termo       = unario { ( "*" | "/" | "%" ) unario } ;
    unario      = ( "-" | "!" ) unario | primario ;
    primario    = NUM | "true" | "false" | ID [ "(" [ args ] ")" ]
                | "(" expr ")" ;
    args        = expr { "," expr } ;
    ID          = letra { letra | digito } ;      (* letra inclui "_" *)
    NUM         = digito { digito } ;
    comentário  = "//" ... fim de linha | "/*" ... "*/" ;

Posições são 1-based (linha, coluna).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ErroMini(Exception):
    """Erro de qualquer etapa do compilador, com posição no fonte."""

    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0,
                 tamanho: int = 1) -> None:
        super().__init__(f"{linha}:{coluna}: {mensagem}")
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.tamanho = max(1, tamanho)


class ErroLexico(ErroMini):
    pass


class TipoToken(Enum):
    NUM = "num"
    ID = "id"
    KEYWORD = "keyword"
    OP = "op"
    EOF = "eof"


@dataclass(frozen=True)
class Token:
    tipo: TipoToken
    lexema: str
    linha: int
    coluna: int


PALAVRAS_CHAVE = frozenset({
    "func", "var", "if", "else", "while", "return", "print",
    "true", "false", "int", "bool", "void",
})
OPERADORES_2 = ("==", "!=", "<=", ">=", "&&", "||", "->")
OPERADORES_1 = "+-*/%<>=!(){},;:"


def _inicio_id(c: str) -> bool:
    return c.isalpha() or c == "_"


def _corpo_id(c: str) -> bool:
    return c.isalnum() or c == "_"


def tokenizar(fonte: str) -> list[Token]:
    """Converte o fonte em tokens, terminando com um token EOF."""
    tokens: list[Token] = []
    i, linha, col = 0, 1, 1
    n = len(fonte)

    def avancar(qtd: int) -> None:
        nonlocal i, linha, col
        for _ in range(qtd):
            if fonte[i] == "\n":
                linha += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        c = fonte[i]
        if c in " \t\r\n":
            avancar(1)
        elif fonte.startswith("//", i):
            while i < n and fonte[i] != "\n":
                avancar(1)
        elif fonte.startswith("/*", i):
            l0, c0 = linha, col
            fim = fonte.find("*/", i + 2)
            if fim < 0:
                raise ErroLexico("comentário de bloco não terminado", l0, c0, 2)
            avancar(fim + 2 - i)
        elif c.isdigit():
            j = i
            while j < n and fonte[j].isdigit():
                j += 1
            if j < n and _inicio_id(fonte[j]):
                k = j
                while k < n and _corpo_id(fonte[k]):
                    k += 1
                raise ErroLexico(f"número malformado '{fonte[i:k]}'",
                                 linha, col, k - i)
            tokens.append(Token(TipoToken.NUM, fonte[i:j], linha, col))
            avancar(j - i)
        elif _inicio_id(c):
            j = i
            while j < n and _corpo_id(fonte[j]):
                j += 1
            lex = fonte[i:j]
            tipo = TipoToken.KEYWORD if lex in PALAVRAS_CHAVE else TipoToken.ID
            tokens.append(Token(tipo, lex, linha, col))
            avancar(j - i)
        elif fonte[i:i + 2] in OPERADORES_2:
            tokens.append(Token(TipoToken.OP, fonte[i:i + 2], linha, col))
            avancar(2)
        elif c in OPERADORES_1:
            tokens.append(Token(TipoToken.OP, c, linha, col))
            avancar(1)
        elif c in "&|":
            raise ErroLexico(f"operador incompleto '{c}' (use '{c}{c}')",
                             linha, col)
        else:
            raise ErroLexico(f"caractere inesperado {c!r}", linha, col)
    tokens.append(Token(TipoToken.EOF, "", linha, col))
    return tokens
