"""Nós da AST de Mini como dataclasses.

Todo nó carrega ``pos`` (linha, coluna) do token que o originou; a posição
não participa da igualdade, então duas árvores com a mesma estrutura são
iguais mesmo vindas de fontes formatados de forma diferente.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

Pos = tuple[int, int]
SEM_POS: Pos = (0, 0)

TIPOS = ("int", "bool", "void")


@dataclass(kw_only=True)
class No:
    pos: Pos = field(default=SEM_POS, compare=False, repr=False)


# --- expressões -----------------------------------------------------------

@dataclass
class Num(No):
    valor: int


@dataclass
class Bool(No):
    valor: bool


@dataclass
class Nome(No):
    nome: str


@dataclass
class Unario(No):
    op: str  # "-" ou "!"
    operando: No


@dataclass
class Binario(No):
    op: str
    esq: No
    dir: No


@dataclass
class Chamada(No):
    nome: str
    args: list[No]


# --- comandos -------------------------------------------------------------

@dataclass
class Bloco(No):
    stmts: list[No]


@dataclass
class Var(No):
    nome: str
    init: No
    tipo: Optional[str] = None  # anotação explícita, se houver


@dataclass
class Atrib(No):
    nome: str
    valor: No


@dataclass
class Se(No):
    cond: No
    entao: Bloco
    senao: Optional[Bloco] = None


@dataclass
class Enquanto(No):
    cond: No
    corpo: Bloco


@dataclass
class Retorno(No):
    valor: Optional[No] = None


@dataclass
class Imprimir(No):
    valor: No


@dataclass
class ExprStmt(No):
    expr: No


# --- declarações de topo --------------------------------------------------

@dataclass
class Param(No):
    nome: str
    tipo: str


@dataclass
class Funcao(No):
    nome: str
    params: list[Param]
    ret: str
    corpo: Bloco


@dataclass
class Programa(No):
    itens: list[No]  # Funcao ou comandos, em ordem de aparição

    def funcoes(self) -> list[Funcao]:
        return [i for i in self.itens if isinstance(i, Funcao)]

    def comandos(self) -> list[No]:
        return [i for i in self.itens if not isinstance(i, Funcao)]


EXPRESSOES = (Num, Bool, Nome, Unario, Binario, Chamada)
