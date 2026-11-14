"""Produtor-consumidor com buffer limitado como simulação de eventos discretos.

Um produtor gera `itens` itens, cada um levando `t_producao`. Consumidores
levam `t_consumo` por item. O item pronto vai direto a um consumidor ocioso
ou ao buffer; se o buffer está cheio o produtor bloqueia segurando o item.
Empates de instante são resolvidos pela ordem de agendamento dos eventos.
"""
from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Resultado:
    fim: int = 0
    consumidos: list[tuple[int, int, int]] = field(default_factory=list)  # (item, consumidor, t_fim)
    produtor_bloqueado: int = 0
    consumidor_ocioso: int = 0  # soma, antes de cada início de consumo
    max_ocupacao: int = 0
    log: list[tuple[int, str]] = field(default_factory=list)


def simular(
    itens: int,
    capacidade: int,
    t_producao: int,
    t_consumo: int,
    consumidores: int = 1,
) -> Resultado:
    if min(itens, capacidade, t_producao, t_consumo, consumidores) <= 0:
        raise ValueError("todos os parâmetros devem ser positivos")
    r = Resultado()
    eventos: list[tuple[int, int, str, tuple]] = []
    seq = 0

    def agendar(t: int, tipo: str, *dados: int) -> None:
        nonlocal seq
        heapq.heappush(eventos, (t, seq, tipo, dados))
        seq += 1

    buffer: deque[int] = deque()
    ociosos: deque[int] = deque(range(consumidores))
    ocioso_desde = {c: 0 for c in range(consumidores)}
    bloqueado: Optional[tuple[int, int]] = None  # (item, desde)
    produzidos = 0

    def produzir(t: int) -> None:
        nonlocal produzidos
        if produzidos < itens:
            produzidos += 1
            agendar(t + t_producao, "produzido", produzidos)

    def consumir(t: int, c: int, item: int) -> None:
        r.consumidor_ocioso += t - ocioso_desde[c]
        r.log.append((t, f"c{c} inicia item {item}"))
        agendar(t + t_consumo, "consumido", c, item)

    produzir(0)
    while eventos:
        t, _, tipo, dados = heapq.heappop(eventos)
        r.fim = t
        if tipo == "produzido":
            (item,) = dados
            r.log.append((t, f"produzido {item}"))
            if ociosos:
                consumir(t, ociosos.popleft(), item)
            elif len(buffer) < capacidade:
                buffer.append(item)
                r.max_ocupacao = max(r.max_ocupacao, len(buffer))
            else:
                bloqueado = (item, t)
                r.log.append((t, f"produtor bloqueia com item {item}"))
                continue
            produzir(t)
        else:
            c, item = dados
            r.consumidos.append((item, c, t))
            r.log.append((t, f"c{c} termina item {item}"))
            ocioso_desde[c] = t  # só conta ociosidade se ele realmente esperar
            if buffer:
                consumir(t, c, buffer.popleft())
                if bloqueado is not None:
                    pendente, desde = bloqueado
                    bloqueado = None
                    r.produtor_bloqueado += t - desde
                    buffer.append(pendente)
                    r.log.append((t, f"produtor libera item {pendente}"))
                    produzir(t)
            else:
                ociosos.append(c)
    return r
