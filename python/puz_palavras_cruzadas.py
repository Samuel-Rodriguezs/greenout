"""Palavras cruzadas: preenchimento de um molde por backtracking com dicionário pequeno."""
from __future__ import annotations

from typing import Optional

Celula = tuple[int, int]
Slot = tuple[Celula, ...]


def extrair_slots(molde: list[str]) -> list[Slot]:
    """Sequências de 2+ células abertas ('.') na horizontal e na vertical; '#' é bloqueio."""
    linhas = len(molde)
    colunas = len(molde[0]) if linhas else 0
    if any(len(l) != colunas for l in molde):
        raise ValueError("molde não retangular")
    slots: list[Slot] = []
    for r in range(linhas):
        c = 0
        while c < colunas:
            if molde[r][c] != "#":
                ini = c
                while c < colunas and molde[r][c] != "#":
                    c += 1
                if c - ini >= 2:
                    slots.append(tuple((r, k) for k in range(ini, c)))
            else:
                c += 1
    for c in range(colunas):
        r = 0
        while r < linhas:
            if molde[r][c] != "#":
                ini = r
                while r < linhas and molde[r][c] != "#":
                    r += 1
                if r - ini >= 2:
                    slots.append(tuple((k, c) for k in range(ini, r)))
            else:
                r += 1
    return slots


def preencher(molde: list[str], dicionario: list[str], unicas: bool = True) -> Optional[list[str]]:
    """Retorna a grade preenchida (linhas de texto, '#' mantido) ou None se não houver solução.

    Células do molde que já contêm letras são respeitadas como pistas.
    """
    slots = extrair_slots(molde)
    palavras = {}
    for p in dicionario:
        palavras.setdefault(len(p), []).append(p.lower())
    grade = {(r, c): ch for r, linha in enumerate(molde) for c, ch in enumerate(linha) if ch != "#"}
    grade = {k: (v if v != "." else "") for k, v in grade.items()}
    usadas: set[str] = set()

    def padrao(slot: Slot) -> list[str]:
        return [grade[c] for c in slot]

    def candidatas(slot: Slot) -> list[str]:
        pad = padrao(slot)
        return [p for p in palavras.get(len(slot), [])
                if all(not ch or ch == pc for ch, pc in zip(pad, p)) and not (unicas and p in usadas)]

    def resolver(restantes: list[Slot]) -> bool:
        if not restantes:
            return True
        # MRV: o slot com menos candidatas; slots já completos são só verificados
        escolhido, melhores = None, None
        for s in restantes:
            cand = candidatas(s)
            if not cand:
                return False
            if melhores is None or len(cand) < len(melhores):
                escolhido, melhores = s, cand
                if len(cand) == 1:
                    break
        resto = [s for s in restantes if s is not escolhido]
        for palavra in melhores:
            novas = [c for c, ch in zip(escolhido, palavra) if not grade[c]]
            for c, ch in zip(escolhido, palavra):
                grade[c] = ch
            usadas.add(palavra)
            if resolver(resto):
                return True
            usadas.discard(palavra)
            for c in novas:
                grade[c] = ""
        return False

    if not resolver(slots):
        return None
    return ["".join("#" if ch == "#" else grade[(r, c)] or " " for c, ch in enumerate(linha))
            for r, linha in enumerate(molde)]


def validar(grade: list[str], dicionario: list[str]) -> bool:
    """Toda sequência de 2+ letras (horizontal/vertical) deve ser palavra do dicionário."""
    molde = ["".join("#" if ch == "#" else "." for ch in l) for l in grade]
    dic = {p.lower() for p in dicionario}
    return all("".join(grade[r][c] for r, c in s) in dic for s in extrair_slots(molde))
