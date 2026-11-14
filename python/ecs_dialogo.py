"""Sistema de diálogos por grafo, com condições, efeitos e variáveis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

Vars = dict[str, object]


@dataclass
class Opcao:
    texto: str
    destino: str | None  # None encerra o diálogo
    condicao: Callable[[Vars], bool] | None = None
    efeito: Callable[[Vars], None] | None = None


@dataclass
class No:
    id: str
    falante: str
    texto: str
    opcoes: list[Opcao] = field(default_factory=list)
    ao_entrar: Callable[[Vars], None] | None = None


class GrafoDialogo:
    def __init__(self) -> None:
        self.nos: dict[str, No] = {}

    def adicionar(self, no: No) -> None:
        if no.id in self.nos:
            raise ValueError(f"nó duplicado: {no.id}")
        self.nos[no.id] = no

    def validar(self, inicio: str) -> list[str]:
        """Problemas do grafo: destinos inexistentes e nós inalcançáveis a partir de `inicio`."""
        erros = []
        if inicio not in self.nos:
            return [f"início inexistente: {inicio}"]
        for no in self.nos.values():
            for op in no.opcoes:
                if op.destino is not None and op.destino not in self.nos:
                    erros.append(f"{no.id}: destino inexistente {op.destino}")
        alcancados, pilha = set(), [inicio]
        while pilha:
            n = pilha.pop()
            if n in alcancados or n not in self.nos:
                continue
            alcancados.add(n)
            pilha.extend(op.destino for op in self.nos[n].opcoes if op.destino)
        erros.extend(f"inalcançável: {i}" for i in sorted(set(self.nos) - alcancados))
        return erros


class Dialogo:
    """Execução de um diálogo: mantém nó atual e variáveis."""

    def __init__(self, grafo: GrafoDialogo, inicio: str, variaveis: Vars | None = None) -> None:
        erros = [e for e in grafo.validar(inicio) if not e.startswith("inalcançável")]
        if erros:
            raise ValueError("; ".join(erros))
        self.grafo = grafo
        self.vars: Vars = dict(variaveis or {})
        self.atual: No | None = None
        self.historico: list[str] = []
        self._ir(inicio)

    def _ir(self, destino: str | None) -> None:
        if destino is None:
            self.atual = None
            return
        self.atual = self.grafo.nos[destino]
        self.historico.append(destino)
        if self.atual.ao_entrar:
            self.atual.ao_entrar(self.vars)

    @property
    def terminou(self) -> bool:
        return self.atual is None

    def opcoes(self) -> list[tuple[int, str]]:
        """(índice original, texto) das opções cujas condições são verdadeiras."""
        if self.atual is None:
            return []
        return [(i, o.texto) for i, o in enumerate(self.atual.opcoes)
                if o.condicao is None or o.condicao(self.vars)]

    def escolher(self, indice: int) -> None:
        if self.atual is None:
            raise RuntimeError("diálogo encerrado")
        if indice not in [i for i, _ in self.opcoes()]:
            raise ValueError(f"opção indisponível: {indice}")
        op = self.atual.opcoes[indice]
        if op.efeito:
            op.efeito(self.vars)
        self._ir(op.destino)

    def continuar(self) -> None:
        """Avança nós sem escolha: com 1 opção disponível segue-a; sem opções, encerra."""
        if self.atual is None:
            raise RuntimeError("diálogo encerrado")
        disp = self.opcoes()
        if not self.atual.opcoes:
            self.atual = None
        elif len(disp) == 1:
            self.escolher(disp[0][0])
        else:
            raise ValueError("há várias opções ou nenhuma disponível: use escolher()")
