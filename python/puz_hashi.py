"""Hashi (Bridges): ilhas com contagem de pontes, 0-2 pontes por par, sem cruzamentos e conexo."""
from __future__ import annotations

from typing import Optional

Ilha = tuple[int, int]
Aresta = tuple[Ilha, Ilha]


def ler_ilhas(linhas: list[str]) -> dict[Ilha, int]:
    """Lê um diagrama onde dígitos 1-8 são ilhas e '.' é água."""
    ilhas = {}
    for r, linha in enumerate(linhas):
        for c, ch in enumerate(linha):
            if ch.isdigit() and ch != "0":
                ilhas[(r, c)] = int(ch)
            elif ch != ".":
                raise ValueError(f"caractere inválido: {ch!r}")
    return ilhas


def arestas_candidatas(ilhas: dict[Ilha, int]) -> list[Aresta]:
    """Pares de ilhas vizinhas em linha reta sem outra ilha entre elas."""
    saida = []
    for (r, c) in sorted(ilhas):
        for dr, dc in ((0, 1), (1, 0)):
            rr, cc = r + dr, c + dc
            limite_r = max(i[0] for i in ilhas)
            limite_c = max(i[1] for i in ilhas)
            while rr <= limite_r and cc <= limite_c:
                if (rr, cc) in ilhas:
                    saida.append(((r, c), (rr, cc)))
                    break
                rr, cc = rr + dr, cc + dc
    return saida


def _cruzam(a: Aresta, b: Aresta) -> bool:
    (r1, c1), (r2, c2) = a
    (r3, c3), (r4, c4) = b
    a_horizontal, b_horizontal = r1 == r2, r3 == r4
    if a_horizontal == b_horizontal:
        return False
    if not a_horizontal:
        (r1, c1), (r2, c2), (r3, c3), (r4, c4) = (r3, c3), (r4, c4), (r1, c1), (r2, c2)
    # agora a = horizontal em r1, b = vertical em c3
    return c1 < c3 < c2 and r3 < r1 < r4


def resolver(ilhas: dict[Ilha, int]) -> Optional[dict[Aresta, int]]:
    """Retorna {aresta: nº de pontes (1 ou 2)} ou None se o puzzle não tem solução."""
    if not ilhas:
        return {}
    if sum(ilhas.values()) % 2:
        return None
    arestas = arestas_candidatas(ilhas)
    incidentes: dict[Ilha, list[int]] = {i: [] for i in ilhas}
    for k, (a, b) in enumerate(arestas):
        incidentes[a].append(k)
        incidentes[b].append(k)
    cruza = [[j for j, o in enumerate(arestas) if j != k and _cruzam(arestas[k], o)]
             for k in range(len(arestas))]
    valor = [-1] * len(arestas)  # -1 = não decidido
    falta = dict(ilhas)          # pontes ainda necessárias por ilha
    livres = {i: len(ks) for i, ks in incidentes.items()}  # arestas ainda não decididas

    def conexo() -> bool:
        adj: dict[Ilha, list[Ilha]] = {i: [] for i in ilhas}
        for k, v in enumerate(valor):
            if v > 0:
                a, b = arestas[k]
                adj[a].append(b)
                adj[b].append(a)
        inicio = next(iter(ilhas))
        vistos, pilha = {inicio}, [inicio]
        while pilha:
            for w in adj[pilha.pop()]:
                if w not in vistos:
                    vistos.add(w)
                    pilha.append(w)
        return len(vistos) == len(ilhas)

    def viavel(i: Ilha) -> bool:
        # as arestas indecididas restantes precisam poder suprir o que falta (até 2 cada)
        return 0 <= falta[i] <= 2 * livres[i]

    def busca(k: int) -> bool:
        if k == len(arestas):
            return all(f == 0 for f in falta.values()) and conexo()
        a, b = arestas[k]
        livres[a] -= 1
        livres[b] -= 1
        for n in (2, 1, 0):
            if n > falta[a] or n > falta[b]:
                continue
            if n and any(valor[j] > 0 for j in cruza[k]):
                continue
            falta[a] -= n
            falta[b] -= n
            valor[k] = n
            if viavel(a) and viavel(b) and busca(k + 1):
                return True
            falta[a] += n
            falta[b] += n
            valor[k] = -1
        livres[a] += 1
        livres[b] += 1
        return False

    if not busca(0):
        return None
    return {arestas[k]: v for k, v in enumerate(valor) if v > 0}


def verificar(ilhas: dict[Ilha, int], pontes: dict[Aresta, int]) -> bool:
    """Confere graus, limite de 2 pontes, ausência de cruzamentos e conectividade."""
    grau = {i: 0 for i in ilhas}
    for (a, b), n in pontes.items():
        if n not in (1, 2) or a not in ilhas or b not in ilhas:
            return False
        grau[a] += n
        grau[b] += n
    if grau != ilhas:
        return False
    lista = list(pontes)
    if any(_cruzam(lista[i], lista[j]) for i in range(len(lista)) for j in range(i + 1, len(lista))):
        return False
    adj: dict[Ilha, set[Ilha]] = {i: set() for i in ilhas}
    for a, b in pontes:
        adj[a].add(b)
        adj[b].add(a)
    inicio = next(iter(ilhas))
    vistos, pilha = {inicio}, [inicio]
    while pilha:
        for w in adj[pilha.pop()]:
            if w not in vistos:
                vistos.add(w)
                pilha.append(w)
    return len(vistos) == len(ilhas)
