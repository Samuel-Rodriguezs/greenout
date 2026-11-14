"""Detecção de deadlock com grafo de alocação de recursos.

Arestas: processo -> recurso (requisição) e recurso -> processo (alocação).
- `ciclo()` procura um ciclo no grafo. Com instância única por recurso, ciclo
  equivale a deadlock; com várias instâncias é só condição necessária.
- `deadlock()` roda o algoritmo de detecção para múltiplas instâncias
  (Disponível/Alocação/Requisição): processos que nunca conseguem terminar.
"""
from __future__ import annotations

from typing import Optional


def detectar_matrizes(
    disponivel: list[int],
    alocacao: list[list[int]],
    requisicao: list[list[int]],
) -> list[int]:
    """Índices dos processos em deadlock (lista vazia = sem deadlock)."""
    trabalho = list(disponivel)
    n = len(alocacao)
    # quem não possui nada não participa de deadlock: pode ser considerado terminado
    terminou = [not any(alocacao[i]) for i in range(n)]
    progresso = True
    while progresso:
        progresso = False
        for i in range(n):
            if not terminou[i] and all(r <= t for r, t in zip(requisicao[i], trabalho)):
                trabalho = [t + a for t, a in zip(trabalho, alocacao[i])]
                terminou[i] = True
                progresso = True
    return [i for i in range(n) if not terminou[i]]


class GrafoAlocacao:
    def __init__(self) -> None:
        self.processos: list[str] = []
        self.instancias: dict[str, int] = {}
        self.alocado: dict[tuple[str, str], int] = {}
        self.requisitado: dict[tuple[str, str], int] = {}

    def processo(self, nome: str) -> None:
        if nome in self.processos or nome in self.instancias:
            raise ValueError(f"nome em uso: {nome}")
        self.processos.append(nome)

    def recurso(self, nome: str, instancias: int = 1) -> None:
        if nome in self.processos or nome in self.instancias:
            raise ValueError(f"nome em uso: {nome}")
        if instancias <= 0:
            raise ValueError("instancias deve ser positivo")
        self.instancias[nome] = instancias

    def livres(self, rec: str) -> int:
        return self.instancias[rec] - sum(n for (_, r), n in self.alocado.items() if r == rec)

    def alocar(self, proc: str, rec: str, n: int = 1) -> None:
        self._validar(proc, rec, n)
        if n > self.livres(rec):
            raise ValueError(f"{rec} não tem {n} instância(s) livre(s)")
        self.alocado[(proc, rec)] = self.alocado.get((proc, rec), 0) + n

    def requisitar(self, proc: str, rec: str, n: int = 1) -> None:
        self._validar(proc, rec, n)
        self.requisitado[(proc, rec)] = self.requisitado.get((proc, rec), 0) + n

    def _validar(self, proc: str, rec: str, n: int) -> None:
        if proc not in self.processos or rec not in self.instancias or n <= 0:
            raise ValueError("processo, recurso ou quantidade inválidos")

    def arestas(self) -> dict[str, list[str]]:
        g: dict[str, list[str]] = {no: [] for no in self.processos + list(self.instancias)}
        for (p, r) in self.requisitado:
            g[p].append(r)
        for (p, r) in self.alocado:
            g[r].append(p)
        return g

    def ciclo(self) -> Optional[list[str]]:
        g = self.arestas()
        estado: dict[str, int] = {}  # 1 = na pilha, 2 = concluído
        pilha: list[str] = []

        def visitar(no: str) -> Optional[list[str]]:
            estado[no] = 1
            pilha.append(no)
            for viz in g[no]:
                if estado.get(viz) == 1:
                    return pilha[pilha.index(viz):]
                if viz not in estado:
                    achou = visitar(viz)
                    if achou:
                        return achou
            pilha.pop()
            estado[no] = 2
            return None

        for no in g:
            if no not in estado:
                achou = visitar(no)
                if achou:
                    return achou
        return None

    def deadlock(self) -> list[str]:
        recs = list(self.instancias)
        disp = [self.livres(r) for r in recs]
        aloc = [[self.alocado.get((p, r), 0) for r in recs] for p in self.processos]
        req = [[self.requisitado.get((p, r), 0) for r in recs] for p in self.processos]
        return [self.processos[i] for i in detectar_matrizes(disp, aloc, req)]
