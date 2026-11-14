"""Semáforos e monitores simulados em passos (sem threads).

Cada processo é um gerador que produz uma instrução por passo. O escalonador
executa uma instrução por vez em rodízio entre os processos prontos, o que
torna as intercalações reproduzíveis.

Instruções: down/up (semáforo contador com fila FIFO e repasse direto),
entrar/sair (exclusão mútua do monitor), esperar/sinalizar/difundir (variáveis
de condição com semântica Mesa: quem é sinalizado volta à fila de entrada do
monitor e precisa reavaliar a condição), passo (evento observável).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Generator, Optional

Instrucao = tuple
Corpo = Callable[[], Generator[Instrucao, None, None]]


def down(sem: str) -> Instrucao:
    return ("down", sem)


def up(sem: str) -> Instrucao:
    return ("up", sem)


def passo(texto: str) -> Instrucao:
    return ("passo", texto)


def entrar(mon: str) -> Instrucao:
    return ("entrar", mon)


def sair(mon: str) -> Instrucao:
    return ("sair", mon)


def esperar(mon: str, cond: str) -> Instrucao:
    return ("esperar", mon, cond)


def sinalizar(mon: str, cond: str) -> Instrucao:
    return ("sinalizar", mon, cond)


def difundir(mon: str, cond: str) -> Instrucao:
    return ("difundir", mon, cond)


class ErroSincronizacao(Exception):
    pass


@dataclass
class _Semaforo:
    valor: int
    fila: deque[str] = field(default_factory=deque)


@dataclass
class _Monitor:
    dono: Optional[str] = None
    entrada: deque[str] = field(default_factory=deque)
    condicoes: dict[str, deque[str]] = field(default_factory=dict)


@dataclass
class _Proc:
    nome: str
    gerador: Generator[Instrucao, None, None]
    estado: str = "pronto"  # pronto | bloqueado | terminado
    motivo: str = ""


class Sistema:
    def __init__(self) -> None:
        self.semaforos: dict[str, _Semaforo] = {}
        self.monitores: dict[str, _Monitor] = {}
        self.procs: list[_Proc] = []
        self.trace: list[tuple[int, str, str]] = []  # (passo, processo, evento)
        self.tempo = 0
        self._ultimo = -1

    # ---------- montagem ----------
    def semaforo(self, nome: str, valor: int = 1) -> None:
        if valor < 0:
            raise ValueError("valor inicial negativo")
        self.semaforos[nome] = _Semaforo(valor)

    def monitor(self, nome: str, condicoes: tuple[str, ...] = ()) -> None:
        self.monitores[nome] = _Monitor(condicoes={c: deque() for c in condicoes})

    def spawn(self, nome: str, corpo: Corpo) -> None:
        if any(p.nome == nome for p in self.procs):
            raise ValueError(f"processo duplicado: {nome}")
        self.procs.append(_Proc(nome, corpo()))

    # ---------- execução ----------
    def _proc(self, nome: str) -> _Proc:
        return next(p for p in self.procs if p.nome == nome)

    def _acordar(self, nome: str) -> None:
        p = self._proc(nome)
        p.estado, p.motivo = "pronto", ""

    def _bloquear(self, p: _Proc, motivo: str) -> None:
        p.estado, p.motivo = "bloqueado", motivo
        self.trace.append((self.tempo, p.nome, f"bloqueia em {motivo}"))

    def _liberar_monitor(self, m: _Monitor) -> None:
        if m.entrada:
            m.dono = m.entrada.popleft()  # repasse direto ao próximo da fila
            self._acordar(m.dono)
        else:
            m.dono = None

    def _executar(self, p: _Proc, ins: Instrucao) -> None:
        op = ins[0]
        if op == "passo":
            self.trace.append((self.tempo, p.nome, ins[1]))
        elif op == "down":
            s = self.semaforos[ins[1]]
            if s.valor > 0:
                s.valor -= 1
            else:
                s.fila.append(p.nome)
                self._bloquear(p, f"semáforo {ins[1]}")
        elif op == "up":
            s = self.semaforos[ins[1]]
            if s.fila:
                self._acordar(s.fila.popleft())  # a vaga vai direto ao acordado
            else:
                s.valor += 1
        elif op in ("entrar", "sair", "esperar", "sinalizar", "difundir"):
            self._executar_monitor(p, ins)
        else:
            raise ErroSincronizacao(f"instrução desconhecida: {ins}")

    def _executar_monitor(self, p: _Proc, ins: Instrucao) -> None:
        op, m = ins[0], self.monitores[ins[1]]
        if op == "entrar":
            if m.dono is None:
                m.dono = p.nome
            else:
                m.entrada.append(p.nome)
                self._bloquear(p, f"monitor {ins[1]}")
            return
        if m.dono != p.nome:
            raise ErroSincronizacao(f"{p.nome} usa {op} sem possuir o monitor {ins[1]}")
        if op == "sair":
            self._liberar_monitor(m)
        elif op == "esperar":
            m.condicoes[ins[2]].append(p.nome)
            self._bloquear(p, f"condição {ins[2]}")
            self._liberar_monitor(m)
        else:
            fila = m.condicoes[ins[2]]
            if op == "sinalizar":
                acordados = [fila.popleft()] if fila else []
            else:
                acordados = list(fila)
                fila.clear()
            for nome in acordados:  # Mesa: vão para a fila de entrada
                m.entrada.append(nome)
                self._proc(nome).motivo = f"monitor {ins[1]}"

    def prontos(self) -> list[str]:
        return [p.nome for p in self.procs if p.estado == "pronto"]

    def bloqueados(self) -> list[str]:
        return [p.nome for p in self.procs if p.estado == "bloqueado"]

    def passo_unico(self) -> bool:
        """Executa uma instrução; False se não há processo pronto."""
        n = len(self.procs)
        for k in range(1, n + 1):
            i = (self._ultimo + k) % n
            p = self.procs[i]
            if p.estado != "pronto":
                continue
            self._ultimo = i
            try:
                ins = next(p.gerador)
            except StopIteration:
                p.estado = "terminado"
                self.trace.append((self.tempo, p.nome, "termina"))
            else:
                self._executar(p, ins)
            self.tempo += 1
            return True
        return False

    def executar(self, max_passos: int = 10_000) -> str:
        """Retorna 'fim', 'deadlock' (todos bloqueados) ou 'limite'."""
        for _ in range(max_passos):
            if not self.passo_unico():
                return "deadlock" if self.bloqueados() else "fim"
        return "limite"

    def eventos(self, processo: Optional[str] = None) -> list[str]:
        """Textos dos eventos 'passo' (exclui bloqueios e términos)."""
        return [
            e
            for _, nome, e in self.trace
            if (processo is None or nome == processo)
            and not e.startswith("bloqueia") and e != "termina"
        ]
