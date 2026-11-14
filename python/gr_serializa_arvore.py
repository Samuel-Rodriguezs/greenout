"""Serialização e desserialização de árvore binária (pré-ordem com marcador nulo)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

NULO = "#"


@dataclass
class No:
    valor: int
    esq: Optional["No"] = None
    dir: Optional["No"] = None


def serializar(raiz: Optional[No]) -> str:
    """Ex.: 1,2,#,#,3,#,# ; árvore vazia vira '#'."""
    partes: list[str] = []
    pilha = [raiz]
    while pilha:
        n = pilha.pop()
        if n is None:
            partes.append(NULO)
        else:
            partes.append(str(n.valor))
            pilha.append(n.dir)
            pilha.append(n.esq)
    return ",".join(partes)


def desserializar(texto: str) -> Optional[No]:
    tokens = texto.split(",")
    if not texto or tokens[0] == "":
        raise ValueError("texto vazio")
    pos = 0
    raiz_falsa = No(0)
    # pilha de (pai, lado) aguardando preenchimento
    pendentes: list[tuple[No, str]] = [(raiz_falsa, "esq")]
    while pendentes:
        if pos >= len(tokens):
            raise ValueError("serialização truncada")
        pai, lado = pendentes.pop()
        tok = tokens[pos]
        pos += 1
        if tok == NULO:
            continue
        try:
            no = No(int(tok))
        except ValueError:
            raise ValueError(f"token inválido: {tok!r}") from None
        setattr(pai, lado, no)
        pendentes.append((no, "dir"))
        pendentes.append((no, "esq"))
    if pos != len(tokens):
        raise ValueError("tokens sobrando")
    return raiz_falsa.esq
