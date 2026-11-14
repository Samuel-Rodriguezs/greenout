"""Caça-palavras: gerador (com seed) e solver nas 8 direções."""
from __future__ import annotations

import random
import string
from typing import Optional

DIRECOES = {
    "E": (0, 1), "O": (0, -1), "S": (1, 0), "N": (-1, 0),
    "SE": (1, 1), "SO": (1, -1), "NE": (-1, 1), "NO": (-1, -1),
}
Posicao = tuple[int, int, str]  # (linha, coluna, direção)


def _normalizar(p: str) -> str:
    return p.strip().upper().replace(" ", "")


def gerar(palavras: list[str], linhas: int, colunas: int, seed: int,
          direcoes: Optional[list[str]] = None) -> tuple[list[list[str]], dict[str, Posicao]]:
    """Posiciona todas as palavras (maiores primeiro) e preenche o resto com letras aleatórias.

    Levanta ValueError se alguma palavra não couber.
    """
    rng = random.Random(seed)
    dirs = direcoes or list(DIRECOES)
    grade: list[list[str]] = [[""] * colunas for _ in range(linhas)]
    posicoes: dict[str, Posicao] = {}
    for original in sorted(palavras, key=lambda p: -len(_normalizar(p))):
        p = _normalizar(original)
        if not p.isalpha():
            raise ValueError(f"palavra inválida: {original!r}")
        candidatos = []
        for r in range(linhas):
            for c in range(colunas):
                for d in dirs:
                    if _cabe(grade, p, r, c, DIRECOES[d]):
                        candidatos.append((r, c, d))
        if not candidatos:
            raise ValueError(f"não coube: {p}")
        r, c, d = rng.choice(candidatos)
        dr, dc = DIRECOES[d]
        for i, ch in enumerate(p):
            grade[r + i * dr][c + i * dc] = ch
        posicoes[p] = (r, c, d)
    for r in range(linhas):
        for c in range(colunas):
            if not grade[r][c]:
                grade[r][c] = rng.choice(string.ascii_uppercase)
    return grade, posicoes


def _cabe(grade: list[list[str]], p: str, r: int, c: int, delta: tuple[int, int]) -> bool:
    dr, dc = delta
    fr, fc = r + (len(p) - 1) * dr, c + (len(p) - 1) * dc
    if not (0 <= fr < len(grade) and 0 <= fc < len(grade[0])):
        return False
    return all(grade[r + i * dr][c + i * dc] in ("", ch) for i, ch in enumerate(p))


def procurar(grade: list[list[str]], palavra: str) -> list[Posicao]:
    """Todas as ocorrências da palavra na grade."""
    p = _normalizar(palavra)
    achados = []
    if not p:
        return achados
    linhas, colunas = len(grade), len(grade[0]) if grade else 0
    for r in range(linhas):
        for c in range(colunas):
            if grade[r][c] != p[0]:
                continue
            for nome, (dr, dc) in DIRECOES.items():
                if len(p) == 1 and nome != "E":
                    continue
                fr, fc = r + (len(p) - 1) * dr, c + (len(p) - 1) * dc
                if 0 <= fr < linhas and 0 <= fc < colunas and \
                        all(grade[r + i * dr][c + i * dc] == ch for i, ch in enumerate(p)):
                    achados.append((r, c, nome))
    return achados


def resolver(grade: list[list[str]], palavras: list[str]) -> dict[str, Optional[Posicao]]:
    """Primeira ocorrência de cada palavra (None se ausente)."""
    saida: dict[str, Optional[Posicao]] = {}
    for p in palavras:
        achados = procurar(grade, p)
        saida[_normalizar(p)] = achados[0] if achados else None
    return saida


def formatar(grade: list[list[str]]) -> str:
    return "\n".join(" ".join(linha) for linha in grade)
