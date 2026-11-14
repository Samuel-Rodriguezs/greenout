"""Quebra-cabeça deslizante (8 e 15 peças) resolvido com A* e distância de Manhattan."""
from __future__ import annotations

import heapq
import random
from typing import Optional

Estado = tuple[int, ...]


def estado_objetivo(lado: int) -> Estado:
    """Peças 1..n*n-1 em ordem e o vazio (0) na última posição."""
    return tuple(range(1, lado * lado)) + (0,)


def manhattan(estado: Estado, lado: int) -> int:
    total = 0
    for i, v in enumerate(estado):
        if v:
            total += abs(i // lado - (v - 1) // lado) + abs(i % lado - (v - 1) % lado)
    return total


def resolvivel(estado: Estado, lado: int) -> bool:
    """Verifica a resolubilidade pela paridade de inversões (e linha do vazio)."""
    pecas = [v for v in estado if v]
    inv = sum(1 for i in range(len(pecas)) for j in range(i + 1, len(pecas)) if pecas[i] > pecas[j])
    if lado % 2 == 1:
        return inv % 2 == 0
    linha_vazio_de_baixo = lado - estado.index(0) // lado
    return (inv + linha_vazio_de_baixo) % 2 == 1


def vizinhos(estado: Estado, lado: int) -> list[tuple[str, Estado]]:
    z = estado.index(0)
    r, c = divmod(z, lado)
    saida = []
    for nome, dr, dc in (("C", -1, 0), ("B", 1, 0), ("E", 0, -1), ("D", 0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < lado and 0 <= nc < lado:
            n = nr * lado + nc
            lista = list(estado)
            lista[z], lista[n] = lista[n], lista[z]
            saida.append((nome, tuple(lista)))
    return saida


def resolver(estado: Estado, lado: int) -> Optional[list[str]]:
    """Retorna a menor sequência de movimentos do vazio (C/B/E/D) ou None."""
    if len(estado) != lado * lado or sorted(estado) != list(range(lado * lado)):
        raise ValueError("estado inválido")
    if not resolvivel(estado, lado):
        return None
    alvo = estado_objetivo(lado)
    contador = 0
    fila = [(manhattan(estado, lado), 0, contador, estado)]
    melhor_g = {estado: 0}
    pai: dict[Estado, tuple[Estado, str]] = {}
    while fila:
        _, g, _, atual = heapq.heappop(fila)
        if atual == alvo:
            caminho = []
            while atual in pai:
                atual, mov = pai[atual][0], pai[atual][1]
                caminho.append(mov)
            return caminho[::-1]
        if g > melhor_g[atual]:
            continue
        for mov, prox in vizinhos(atual, lado):
            ng = g + 1
            if ng < melhor_g.get(prox, 1 << 30):
                melhor_g[prox] = ng
                pai[prox] = (atual, mov)
                contador += 1
                heapq.heappush(fila, (ng + manhattan(prox, lado), ng, contador, prox))
    return None


def embaralhar(lado: int, passos: int, seed: int) -> Estado:
    """Embaralha com movimentos válidos, garantindo resolubilidade."""
    rng = random.Random(seed)
    estado = estado_objetivo(lado)
    for _ in range(passos):
        estado = rng.choice(vizinhos(estado, lado))[1]
    return estado


def aplicar(estado: Estado, lado: int, movimentos: list[str]) -> Estado:
    for m in movimentos:
        estado = dict(vizinhos(estado, lado))[m]
    return estado
