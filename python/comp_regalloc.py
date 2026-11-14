"""Alocação de registradores por coloração de grafo (Chaitin-Briggs otimista).

1. Grafo de interferência: uma definição ``d`` interfere com tudo que está vivo
   logo depois dela (exceto a origem, em cópias ``d = s``); as variáveis vivas
   na entrada da função (parâmetros) interferem entre si.
2. Simplificar: remove nós de grau < k empilhando-os; se não houver, empilha o
   de maior grau como candidato a derramamento (spill) e segue otimista.
3. Selecionar: desempilha atribuindo a menor cor livre; sem cor livre, o nome
   é derramado para memória.

``renomear`` reescreve o TAC com ``r0..r{k-1}`` e ``m0..`` (memória).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from comp_blocos import CFG, construir_cfg
from comp_tac import (Bin, Chama, Copia, FuncaoTAC, Imprime, Instrucao, Param,
                      Retorna, SaltoSeNao, Un, definido, usados)
from comp_vivacidade import Vivacidade, analisar_vivacidade, pontos_vivos

Grafo = dict[str, set[str]]


@dataclass
class Alocacao:
    k: int
    cores: dict[str, int] = field(default_factory=dict)
    derramados: set[str] = field(default_factory=set)

    @property
    def registradores_usados(self) -> int:
        return len(set(self.cores.values()))


def grafo_de_interferencia(cfg: CFG, viv: Optional[Vivacidade] = None) -> Grafo:
    viv = viv or analisar_vivacidade(cfg)
    g: Grafo = {}

    def no(n: str) -> None:
        g.setdefault(n, set())

    def aresta(a: str, b: str) -> None:
        if a != b:
            no(a)
            no(b)
            g[a].add(b)
            g[b].add(a)

    for b in cfg.blocos:
        for i in b.instrs:
            for n in usados(i):
                no(n)
            d = definido(i)
            if d is not None:
                no(d)
    entrada = sorted(viv.entrada[0])
    for x in range(len(entrada)):
        for y in range(x + 1, len(entrada)):
            aresta(entrada[x], entrada[y])
    for pontos in pontos_vivos(cfg, viv).values():
        for p in pontos:
            d = definido(p.instrucao)
            if d is None:
                continue
            origem = p.instrucao.src if isinstance(p.instrucao, Copia) else None
            for v in p.depois:
                if v != d and v != origem:
                    aresta(d, v)
    return g


def colorir(grafo: Grafo, k: int) -> Alocacao:
    """Colore o grafo com k cores; nós sem cor ficam em ``derramados``."""
    restantes = {n: set(vs) for n, vs in grafo.items()}
    pilha: list[str] = []
    while restantes:
        candidatos = sorted(n for n, vs in restantes.items() if len(vs) < k)
        if candidatos:
            escolhido = candidatos[0]
        else:  # derramamento potencial: o de maior grau (desempate pelo nome)
            escolhido = max(sorted(restantes), key=lambda n: len(restantes[n]))
        pilha.append(escolhido)
        for v in restantes.pop(escolhido):
            restantes[v].discard(escolhido)
    aloc = Alocacao(k)
    while pilha:
        n = pilha.pop()
        usadas = {aloc.cores[v] for v in grafo[n] if v in aloc.cores}
        livre = next((c for c in range(k) if c not in usadas), None)
        if livre is None:
            aloc.derramados.add(n)
        else:
            aloc.cores[n] = livre
    return aloc


def coloracao_valida(grafo: Grafo, aloc: Alocacao) -> bool:
    return all(aloc.cores[a] != aloc.cores[b]
               for a, vs in grafo.items() for b in vs
               if a in aloc.cores and b in aloc.cores)


def alocar(codigo: list[Instrucao], k: int, params: Optional[list[str]] = None
           ) -> tuple[Alocacao, Grafo]:
    cfg = construir_cfg(codigo)
    viv = analisar_vivacidade(cfg)
    grafo = grafo_de_interferencia(cfg, viv)
    ps = params or []
    for p in ps:  # os argumentos chegam todos juntos: nunca compartilham registrador
        grafo.setdefault(p, set()).update(q for q in ps if q != p)
    return colorir(grafo, k), grafo


def _mapa_nomes(aloc: Alocacao) -> dict[str, str]:
    memoria = {n: i for i, n in enumerate(sorted(aloc.derramados))}
    mapa = {n: f"r{c}" for n, c in aloc.cores.items()}
    mapa.update({n: f"m{memoria[n]}" for n in aloc.derramados})
    return mapa


def renomear(f: FuncaoTAC, aloc: Alocacao) -> FuncaoTAC:
    """Nova função TAC em que cada nome virou registrador (rN) ou memória (mN)."""
    mapa = _mapa_nomes(aloc)

    def o(x: object) -> object:
        return mapa[x] if isinstance(x, str) else x

    novo: list[Instrucao] = []
    for i in f.codigo:
        if isinstance(i, Copia):
            novo.append(Copia(mapa[i.dest], o(i.src)))
        elif isinstance(i, Bin):
            novo.append(Bin(mapa[i.dest], i.op, o(i.a), o(i.b)))
        elif isinstance(i, Un):
            novo.append(Un(mapa[i.dest], i.op, o(i.a)))
        elif isinstance(i, SaltoSeNao):
            novo.append(SaltoSeNao(o(i.cond), i.alvo))
        elif isinstance(i, Param):
            novo.append(Param(o(i.valor)))
        elif isinstance(i, Chama):
            novo.append(Chama(mapa[i.dest], i.func, i.n_args))
        elif isinstance(i, Retorna):
            novo.append(Retorna(o(i.valor) if i.valor is not None else None))
        elif isinstance(i, Imprime):
            novo.append(Imprime(o(i.valor)))
        else:
            novo.append(i)
    return FuncaoTAC(f.nome, [mapa[p] for p in f.params], novo)
