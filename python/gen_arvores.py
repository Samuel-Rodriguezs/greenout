"""Árvores aleatórias: uniforme por código de Prüfer e árvore binária de busca por inserção aleatória."""
from __future__ import annotations

import heapq
import random
from dataclasses import dataclass


def codigo_prufer(rng: random.Random, n: int) -> list[int]:
    """Sequência de n-2 rótulos em 0..n-1; cada árvore rotulada tem a mesma probabilidade."""
    if n < 2:
        raise ValueError("n deve ser >= 2")
    return [rng.randrange(n) for _ in range(n - 2)]


def prufer_para_arestas(codigo: list[int], n: int) -> list[tuple[int, int]]:
    """Decodifica um código de Prüfer em n-1 arestas (u < v)."""
    if len(codigo) != n - 2 or any(not 0 <= x < n for x in codigo):
        raise ValueError("código de Prüfer inválido")
    grau = [1] * n
    for x in codigo:
        grau[x] += 1
    folhas = [i for i in range(n) if grau[i] == 1]
    heapq.heapify(folhas)
    arestas: list[tuple[int, int]] = []
    for x in codigo:
        folha = heapq.heappop(folhas)
        arestas.append((min(folha, x), max(folha, x)))
        grau[x] -= 1
        if grau[x] == 1:
            heapq.heappush(folhas, x)
    u, v = heapq.heappop(folhas), heapq.heappop(folhas)
    arestas.append((min(u, v), max(u, v)))
    return arestas


def arvore_uniforme(rng: random.Random, n: int) -> list[tuple[int, int]]:
    if n == 2:
        return [(0, 1)]
    return prufer_para_arestas(codigo_prufer(rng, n), n)


@dataclass
class No:
    chave: int
    esq: "No | None" = None
    dir: "No | None" = None


def inserir(raiz: No | None, chave: int) -> No:
    if raiz is None:
        return No(chave)
    atual = raiz
    while True:
        if chave < atual.chave:
            if atual.esq is None:
                atual.esq = No(chave)
                break
            atual = atual.esq
        elif chave > atual.chave:
            if atual.dir is None:
                atual.dir = No(chave)
                break
            atual = atual.dir
        else:
            break  # chave repetida ignorada
    return raiz


def bst_aleatoria(rng: random.Random, n: int) -> No | None:
    """BST com as chaves 0..n-1 inseridas em ordem aleatória (altura esperada O(log n))."""
    chaves = list(range(n))
    rng.shuffle(chaves)
    raiz: No | None = None
    for c in chaves:
        raiz = inserir(raiz, c)
    return raiz


def em_ordem(raiz: No | None) -> list[int]:
    saida: list[int] = []
    pilha: list[No] = []
    atual = raiz
    while pilha or atual:
        while atual:
            pilha.append(atual)
            atual = atual.esq
        atual = pilha.pop()
        saida.append(atual.chave)
        atual = atual.dir
    return saida


def altura(raiz: No | None) -> int:
    """Número de níveis (árvore vazia = 0)."""
    nivel = [raiz] if raiz else []
    h = 0
    while nivel:
        h += 1
        nivel = [f for no in nivel for f in (no.esq, no.dir) if f]
    return h
