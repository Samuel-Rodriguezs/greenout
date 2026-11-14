"""Tabela de processos com fork/exec/wait/exit e sinais, tudo simulado.

Segue a semântica POSIX básica:
- fork copia o PCB (programa e disposições de sinais); o filho recebe novo pid;
- exec troca o programa e restaura handlers capturados ao padrão (ignorados persistem);
- exit vira zumbi até o pai fazer wait; filhos órfãos são adotados pelo init (pid 1);
- SIGKILL e SIGSTOP não podem ser capturados, ignorados nem bloqueados;
- sinais padrão bloqueados ficam pendentes e não se acumulam (um bit por sinal).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Union

SIGINT, SIGKILL, SIGUSR1, SIGTERM, SIGCHLD, SIGCONT, SIGSTOP = 2, 9, 10, 15, 17, 18, 19
SIG_DFL = "dfl"
SIG_IGN = "ign"
Disposicao = Union[str, Callable[[int], None]]

_NAO_CAPTURAVEIS = (SIGKILL, SIGSTOP)
_PADRAO_TERMINA = (SIGINT, SIGTERM, SIGUSR1, SIGKILL)


class ErroECHILD(Exception):
    """wait sem filhos."""


class ProcessoInexistente(Exception):
    pass


@dataclass(frozen=True)
class Saida:
    pid: int
    status: int  # código de saída, ou 128 + sinal se morto por sinal
    sinal: Optional[int] = None


@dataclass
class PCB:
    pid: int
    ppid: int
    programa: str
    estado: str = "pronto"  # pronto, bloqueado (em wait), parado, zumbi
    handlers: dict[int, Disposicao] = field(default_factory=dict)
    bloqueados: set[int] = field(default_factory=set)
    pendentes: set[int] = field(default_factory=set)
    saida: Optional[Saida] = None
    wait_resultado: Optional[Saida] = None
    esperando: Optional[int] = None  # pid específico do wait, se houver


class Kernel:
    def __init__(self) -> None:
        self.tabela: dict[int, PCB] = {1: PCB(1, 0, "init")}
        self._proximo = 2

    def _pcb(self, pid: int) -> PCB:
        if pid not in self.tabela:
            raise ProcessoInexistente(pid)
        return self.tabela[pid]

    def filhos(self, pid: int) -> list[int]:
        return sorted(p.pid for p in self.tabela.values() if p.ppid == pid)

    # ---------- ciclo de vida ----------
    def fork(self, pid: int) -> int:
        pai = self._pcb(pid)
        if pai.estado == "zumbi":
            raise ProcessoInexistente(pid)
        filho = PCB(self._proximo, pid, pai.programa, handlers=dict(pai.handlers),
                    bloqueados=set(pai.bloqueados))  # pendentes não são herdados
        self.tabela[filho.pid] = filho
        self._proximo += 1
        return filho.pid

    def exec(self, pid: int, programa: str) -> None:
        p = self._pcb(pid)
        p.programa = programa
        p.handlers = {s: d for s, d in p.handlers.items() if d == SIG_IGN}

    def exit(self, pid: int, status: int = 0, sinal: Optional[int] = None) -> None:
        p = self._pcb(pid)
        if pid == 1:
            raise ValueError("init não pode terminar")
        if p.estado == "zumbi":
            return
        for filho in self.filhos(pid):
            self.tabela[filho].ppid = 1  # adoção pelo init
        p.estado = "zumbi"
        p.saida = Saida(pid, status if sinal is None else 128 + sinal, sinal)
        self.kill(p.ppid, SIGCHLD)
        pai = self.tabela[p.ppid]
        if pai.estado == "bloqueado" and pai.esperando in (None, pid):
            pai.wait_resultado = self._colher(pai, p)
            pai.estado, pai.esperando = "pronto", None

    def _colher(self, pai: PCB, zumbi: PCB) -> Saida:
        assert zumbi.saida is not None
        del self.tabela[zumbi.pid]
        return zumbi.saida

    def wait(self, pid: int, filho: Optional[int] = None) -> Optional[Saida]:
        """Devolve o filho colhido ou None se o processo bloqueou esperando."""
        p = self._pcb(pid)
        candidatos = [f for f in self.filhos(pid) if filho is None or f == filho]
        if not candidatos:
            raise ErroECHILD(pid)
        for f in candidatos:
            if self.tabela[f].estado == "zumbi":
                return self._colher(p, self.tabela[f])
        p.estado, p.esperando = "bloqueado", filho
        return None

    # ---------- sinais ----------
    def sigaction(self, pid: int, sinal: int, disposicao: Disposicao) -> None:
        if sinal in _NAO_CAPTURAVEIS:
            raise ValueError(f"sinal {sinal} não pode ser capturado nem ignorado")
        p = self._pcb(pid)
        if disposicao == SIG_DFL:
            p.handlers.pop(sinal, None)
        else:
            p.handlers[sinal] = disposicao

    def bloquear(self, pid: int, sinal: int) -> None:
        if sinal in _NAO_CAPTURAVEIS:
            raise ValueError(f"sinal {sinal} não pode ser bloqueado")
        self._pcb(pid).bloqueados.add(sinal)

    def desbloquear(self, pid: int, sinal: int) -> None:
        p = self._pcb(pid)
        p.bloqueados.discard(sinal)
        if sinal in p.pendentes:
            p.pendentes.discard(sinal)
            self._entregar(p, sinal)

    def kill(self, pid: int, sinal: int) -> None:
        p = self._pcb(pid)
        if p.estado == "zumbi":
            return
        if sinal in p.bloqueados:
            p.pendentes.add(sinal)
            return
        self._entregar(p, sinal)

    def _entregar(self, p: PCB, sinal: int) -> None:
        if sinal == SIGKILL:
            self.exit(p.pid, sinal=SIGKILL)
        elif sinal == SIGSTOP:
            p.estado = "parado"
        elif sinal == SIGCONT:
            if p.estado == "parado":
                p.estado = "pronto"
            handler = p.handlers.get(sinal)
            if callable(handler):
                handler(sinal)
        else:
            d = p.handlers.get(sinal, SIG_DFL)
            if d == SIG_IGN:
                return
            if callable(d):
                d(sinal)
            elif sinal in _PADRAO_TERMINA and p.pid != 1:
                self.exit(p.pid, sinal=sinal)

    def ps(self) -> list[tuple[int, int, str, str]]:
        return [(p.pid, p.ppid, p.estado, p.programa) for p in sorted(self.tabela.values(), key=lambda p: p.pid)]
