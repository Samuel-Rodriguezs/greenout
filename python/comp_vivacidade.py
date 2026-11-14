"""Análise de vivacidade (liveness) sobre o CFG de TAC.

Equações (análise para trás, ponto fixo iterativo)::

    vivas_saida[B]   = união de vivas_entrada[S] para cada sucessor S de B
    vivas_entrada[B] = uso[B] ∪ (vivas_saida[B] − def[B])

onde ``uso[B]`` são os nomes lidos antes de qualquer escrita em B e ``def[B]``
os nomes escritos em B. Também calcula os conjuntos por instrução.
"""
from __future__ import annotations

from dataclasses import dataclass

from comp_blocos import BlocoBasico, CFG
from comp_tac import Instrucao, definido, usados


@dataclass
class Vivacidade:
    uso: dict[int, set[str]]
    defs: dict[int, set[str]]
    entrada: dict[int, set[str]]
    saida: dict[int, set[str]]


@dataclass(frozen=True)
class PontoVivo:
    instrucao: Instrucao
    antes: frozenset[str]  # vivas imediatamente antes da instrução
    depois: frozenset[str]  # vivas imediatamente depois dela


def _uso_def(b: BlocoBasico) -> tuple[set[str], set[str]]:
    uso: set[str] = set()
    defs: set[str] = set()
    for i in b.instrs:
        uso.update(n for n in usados(i) if n not in defs)
        d = definido(i)
        if d is not None:
            defs.add(d)
    return uso, defs


def analisar_vivacidade(cfg: CFG) -> Vivacidade:
    uso: dict[int, set[str]] = {}
    defs: dict[int, set[str]] = {}
    for b in cfg.blocos:
        uso[b.id], defs[b.id] = _uso_def(b)
    entrada = {b.id: set() for b in cfg.blocos}
    saida = {b.id: set() for b in cfg.blocos}
    mudou = True
    while mudou:
        mudou = False
        for b in reversed(cfg.blocos):
            nova_saida: set[str] = set()
            for s in b.sucessores:
                nova_saida |= entrada[s]
            nova_entrada = uso[b.id] | (nova_saida - defs[b.id])
            if nova_saida != saida[b.id] or nova_entrada != entrada[b.id]:
                saida[b.id], entrada[b.id] = nova_saida, nova_entrada
                mudou = True
    return Vivacidade(uso, defs, entrada, saida)


def pontos_vivos(cfg: CFG, viv: Vivacidade) -> dict[int, list[PontoVivo]]:
    """Vivas antes/depois de cada instrução, na ordem do bloco."""
    resultado: dict[int, list[PontoVivo]] = {}
    for b in cfg.blocos:
        vivas = set(viv.saida[b.id])
        pontos: list[PontoVivo] = []
        for i in reversed(b.instrs):
            depois = frozenset(vivas)
            d = definido(i)
            if d is not None:
                vivas.discard(d)
            vivas.update(usados(i))
            pontos.append(PontoVivo(i, frozenset(vivas), depois))
        resultado[b.id] = pontos[::-1]
    return resultado


def definicoes_mortas(cfg: CFG, viv: Vivacidade) -> list[Instrucao]:
    """Instruções que escrevem um nome que nunca será lido depois (sem efeito colateral)."""
    from comp_tac import Chama
    mortas: list[Instrucao] = []
    for pontos in pontos_vivos(cfg, viv).values():
        for p in pontos:
            d = definido(p.instrucao)
            if d is not None and d not in p.depois and not isinstance(p.instrucao, Chama):
                mortas.append(p.instrucao)
    return mortas
