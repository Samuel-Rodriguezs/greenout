"""Escalonamento de braço de disco: FCFS, SSTF, SCAN, C-SCAN, LOOK e C-LOOK.

O resultado traz a ordem de atendimento, o percurso completo do cabeçote
(incluindo as extremidades visitadas por SCAN/C-SCAN e o salto de retorno do
C-SCAN/C-LOOK, que conta como movimento) e a distância total percorrida.
"""
from __future__ import annotations

from dataclasses import dataclass

ALGORITMOS = ("fcfs", "sstf", "scan", "cscan", "look", "clook")


@dataclass(frozen=True)
class Resultado:
    algoritmo: str
    atendimento: tuple[int, ...]
    percurso: tuple[int, ...]
    movimento: int


def _movimento(percurso: list[int]) -> int:
    return sum(abs(a - b) for a, b in zip(percurso, percurso[1:]))


def escalonar(
    pedidos: list[int],
    inicio: int,
    algoritmo: str,
    direcao: str = "cima",
    cilindros: int = 200,
) -> Resultado:
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"algoritmo desconhecido: {algoritmo}")
    if direcao not in ("cima", "baixo"):
        raise ValueError("direcao deve ser 'cima' ou 'baixo'")
    if not 0 <= inicio < cilindros or any(not 0 <= p < cilindros for p in pedidos):
        raise ValueError("cilindro fora do intervalo")
    ultimo = cilindros - 1
    if not pedidos:
        return Resultado(algoritmo, (), (inicio,), 0)

    if algoritmo == "fcfs":
        atend = list(pedidos)
        percurso = [inicio] + atend
    elif algoritmo == "sstf":
        restantes = list(pedidos)
        atend, pos = [], inicio
        while restantes:
            i = min(range(len(restantes)), key=lambda k: (abs(restantes[k] - pos), k))
            pos = restantes.pop(i)
            atend.append(pos)
        percurso = [inicio] + atend
    else:
        acima = sorted(p for p in pedidos if p >= inicio)
        abaixo = sorted((p for p in pedidos if p < inicio), reverse=True)
        subindo = direcao == "cima"
        primeiro = acima if subindo else abaixo
        segundo = abaixo if subindo else acima
        borda_fim = ultimo if subindo else 0
        borda_ini = 0 if subindo else ultimo
        if algoritmo in ("scan", "look"):
            atend = primeiro + segundo
            percurso = [inicio] + primeiro
            if algoritmo == "scan":
                percurso.append(borda_fim)  # SCAN vai sempre até a extremidade
            percurso += segundo
        else:  # cscan / clook: volta ao outro extremo e continua no mesmo sentido
            volta = segundo[::-1]
            atend = primeiro + volta
            percurso = [inicio] + primeiro
            if algoritmo == "cscan":
                percurso.append(borda_fim)
            if volta:
                if algoritmo == "cscan":
                    percurso.append(borda_ini)  # salto de retorno
                percurso += volta
    return Resultado(algoritmo, tuple(atend), tuple(percurso), _movimento(percurso))
