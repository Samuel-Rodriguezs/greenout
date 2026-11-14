"""Escalonamento de CPU simulado: FCFS, SJF (não preemptivo) e SRTF (preemptivo).

A simulação avança de 1 em 1 unidade de tempo, é determinística e gera uma
linha do tempo, da qual saem o diagrama de Gantt em texto e as métricas de
tempo de espera e de retorno. Desempates: menor chegada, depois ordem de entrada.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class Processo:
    pid: str
    chegada: int
    surto: int  # tempo de CPU necessário
    prioridade: int = 0


@dataclass(frozen=True)
class Resultado:
    linha_tempo: tuple[Optional[str], ...]  # um pid (ou None = ocioso) por unidade
    conclusao: dict[str, int]
    espera: dict[str, int]
    retorno: dict[str, int]

    @property
    def espera_media(self) -> float:
        return sum(self.espera.values()) / len(self.espera)

    @property
    def retorno_medio(self) -> float:
        return sum(self.retorno.values()) / len(self.retorno)

    def segmentos(self) -> list[tuple[Optional[str], int, int]]:
        return segmentos(self.linha_tempo)


def segmentos(linha: tuple[Optional[str], ...]) -> list[tuple[Optional[str], int, int]]:
    """Comprime a linha do tempo em (pid, início, fim)."""
    saida: list[tuple[Optional[str], int, int]] = []
    for t, pid in enumerate(linha):
        if saida and saida[-1][0] == pid:
            saida[-1] = (pid, saida[-1][1], t + 1)
        else:
            saida.append((pid, t, t + 1))
    return saida


def gantt(linha: tuple[Optional[str], ...]) -> str:
    """Diagrama de Gantt em duas linhas: blocos e marcas de tempo."""
    blocos = ""
    marcas = ""
    for pid, ini, fim in segmentos(linha):
        nome = pid if pid is not None else "--"
        largura = max(len(nome) + 2, len(str(ini)) + 1)
        blocos += "|" + nome.center(largura)
        marcas += str(ini).ljust(largura + 1)
    blocos += "|"
    marcas += str(len(linha))
    return blocos + "\n" + marcas


def metricas(procs: list[Processo], linha: tuple[Optional[str], ...]) -> Resultado:
    conclusao: dict[str, int] = {}
    for t, pid in enumerate(linha):
        if pid is not None:
            conclusao[pid] = t + 1
    retorno = {p.pid: conclusao[p.pid] - p.chegada for p in procs}
    espera = {p.pid: retorno[p.pid] - p.surto for p in procs}
    return Resultado(linha, conclusao, espera, retorno)


def validar(procs: list[Processo]) -> None:
    if not procs:
        raise ValueError("lista de processos vazia")
    if len({p.pid for p in procs}) != len(procs):
        raise ValueError("pids duplicados")
    for p in procs:
        if p.surto <= 0 or p.chegada < 0:
            raise ValueError(f"processo inválido: {p.pid}")


def _simular(
    procs: list[Processo],
    chave: Callable[[Processo, int], tuple],
    preemptivo: bool,
) -> Resultado:
    validar(procs)
    restante = {p.pid: p.surto for p in procs}
    ordem = {p.pid: i for i, p in enumerate(procs)}
    linha: list[Optional[str]] = []
    atual: Optional[Processo] = None
    t = 0
    while any(r > 0 for r in restante.values()):
        prontos = [p for p in procs if p.chegada <= t and restante[p.pid] > 0]
        if not prontos:
            linha.append(None)
            atual = None
            t += 1
            continue
        if preemptivo or atual is None or restante[atual.pid] == 0:
            atual = min(
                prontos,
                key=lambda p: (*chave(p, restante[p.pid]), p.chegada, ordem[p.pid]),
            )
        linha.append(atual.pid)
        restante[atual.pid] -= 1
        t += 1
    return metricas(procs, tuple(linha))


def fcfs(procs: list[Processo]) -> Resultado:
    return _simular(procs, lambda p, r: (p.chegada,), preemptivo=False)


def sjf(procs: list[Processo]) -> Resultado:
    return _simular(procs, lambda p, r: (p.surto,), preemptivo=False)


def srtf(procs: list[Processo]) -> Resultado:
    return _simular(procs, lambda p, r: (r,), preemptivo=True)
