"""Blocos básicos e grafo de fluxo de controle (CFG) a partir do TAC de Mini.

Líderes: a primeira instrução, todo rótulo e a instrução seguinte a um salto
ou retorno. Arestas: ``goto`` leva ao bloco do rótulo, ``ifFalse`` tem dois
sucessores (queda e destino), ``return`` não tem sucessor e as demais
instruções caem no bloco seguinte.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from comp_tac import Instrucao, Retorna, Rotulo, Salto, SaltoSeNao


@dataclass
class BlocoBasico:
    id: int
    instrs: list[Instrucao]
    sucessores: list[int] = field(default_factory=list)
    predecessores: list[int] = field(default_factory=list)

    @property
    def rotulo(self) -> Optional[str]:
        i = self.instrs[0] if self.instrs else None
        return i.nome if isinstance(i, Rotulo) else None


@dataclass
class CFG:
    blocos: list[BlocoBasico]

    @property
    def entrada(self) -> BlocoBasico:
        return self.blocos[0]

    def bloco(self, id_: int) -> BlocoBasico:
        return self.blocos[id_]


def construir_cfg(codigo: list[Instrucao]) -> CFG:
    if not codigo:
        return CFG([BlocoBasico(0, [])])
    lideres = {0}
    for k, i in enumerate(codigo):
        if isinstance(i, Rotulo):
            lideres.add(k)
        if isinstance(i, (Salto, SaltoSeNao, Retorna)) and k + 1 < len(codigo):
            lideres.add(k + 1)
    inicios = sorted(lideres)
    blocos = [BlocoBasico(n, codigo[a:(inicios[n + 1] if n + 1 < len(inicios) else len(codigo))])
              for n, a in enumerate(inicios)]
    por_rotulo = {b.rotulo: b.id for b in blocos if b.rotulo is not None}

    for b in blocos:
        ultimo = b.instrs[-1]
        queda = b.id + 1 if b.id + 1 < len(blocos) else None
        alvos: list[int] = []
        if isinstance(ultimo, Salto):
            alvos = [por_rotulo[ultimo.alvo]]
        elif isinstance(ultimo, SaltoSeNao):
            alvos = ([queda] if queda is not None else []) + [por_rotulo[ultimo.alvo]]
        elif isinstance(ultimo, Retorna):
            alvos = []
        elif queda is not None:
            alvos = [queda]
        for a in alvos:
            if a not in b.sucessores:
                b.sucessores.append(a)
    for b in blocos:
        for s in b.sucessores:
            blocos[s].predecessores.append(b.id)
    return CFG(blocos)


def alcancaveis(cfg: CFG) -> set[int]:
    visto: set[int] = set()
    pilha = [0]
    while pilha:
        n = pilha.pop()
        if n in visto:
            continue
        visto.add(n)
        pilha.extend(cfg.blocos[n].sucessores)
    return visto


def ordem_pos_ordem_reversa(cfg: CFG) -> list[int]:
    """Ordem reversa da pós-ordem de uma DFS: bom para análises para frente."""
    visto: set[int] = set()
    pos: list[int] = []

    def dfs(n: int) -> None:
        visto.add(n)
        for s in cfg.blocos[n].sucessores:
            if s not in visto:
                dfs(s)
        pos.append(n)

    dfs(0)
    return pos[::-1]


def dominadores(cfg: CFG) -> dict[int, set[int]]:
    """Conjunto de dominadores de cada bloco alcançável (algoritmo iterativo)."""
    nos = ordem_pos_ordem_reversa(cfg)
    todos = set(nos)
    dom = {n: set(todos) for n in nos}
    dom[0] = {0}
    mudou = True
    while mudou:
        mudou = False
        for n in nos:
            if n == 0:
                continue
            preds = [p for p in cfg.blocos[n].predecessores if p in dom]
            novo = {n} | (set.intersection(*(dom[p] for p in preds)) if preds else set())
            if novo != dom[n]:
                dom[n] = novo
                mudou = True
    return dom


def arestas_de_retorno(cfg: CFG) -> list[tuple[int, int]]:
    """Arestas (u, v) em que v domina u: cada uma fecha um laço natural."""
    dom = dominadores(cfg)
    return [(u, v) for u in dom for v in cfg.blocos[u].sucessores if v in dom[u]]


def remover_inalcancaveis(cfg: CFG) -> CFG:
    vivos = alcancaveis(cfg)
    return construir_cfg(linearizar(cfg, vivos))


def linearizar(cfg: CFG, apenas: Optional[set[int]] = None) -> list[Instrucao]:
    codigo: list[Instrucao] = []
    for b in cfg.blocos:
        if apenas is None or b.id in apenas:
            codigo.extend(b.instrs)
    return codigo


def para_dot(cfg: CFG, nome: str = "cfg") -> str:
    from comp_tac import formatar_instrucao
    linhas = [f"digraph {nome} {{", "  node [shape=box, fontname=monospace];"]
    for b in cfg.blocos:
        texto = "\\l".join(formatar_instrucao(i).replace('"', "'") for i in b.instrs)
        linhas.append(f'  B{b.id} [label="B{b.id}\\n{texto}\\l"];')
    for b in cfg.blocos:
        for s in b.sucessores:
            linhas.append(f"  B{b.id} -> B{s};")
    linhas.append("}")
    return "\n".join(linhas)
