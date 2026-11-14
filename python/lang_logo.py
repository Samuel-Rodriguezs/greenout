"""Interpretador de comandos tipo Logo: tartaruga em grade, com REPEAT aninhado.

Comandos: FORWARD n (FD), BACK n (BK), LEFT (LT), RIGHT (RT) [giros de 90 graus],
PENUP (PU), PENDOWN (PD), REPEAT n [ ... ], HOME. Direção inicial: norte; (0,0) é a origem,
y cresce para o norte.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class ErroLogo(Exception):
    """Erro de sintaxe ou execução."""


_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, L, S, O
_ALIAS = {"FD": "FORWARD", "BK": "BACK", "LT": "LEFT", "RT": "RIGHT", "PU": "PENUP", "PD": "PENDOWN"}


@dataclass
class Tartaruga:
    x: int = 0
    y: int = 0
    direcao: int = 0  # índice em _DIRS
    caneta: bool = True
    riscados: set[tuple[int, int]] = field(default_factory=lambda: {(0, 0)})
    passos: int = 0

    def mover(self, n: int, sentido: int) -> None:
        dx, dy = _DIRS[self.direcao]
        for _ in range(n):
            self.x += dx * sentido
            self.y += dy * sentido
            if self.caneta:
                self.riscados.add((self.x, self.y))


def _tokens(fonte: str) -> list[str]:
    fonte = "\n".join(l.split(";", 1)[0] for l in fonte.splitlines())
    return fonte.replace("[", " [ ").replace("]", " ] ").upper().split()


def _inteiro(tok: str | None, cmd: str) -> int:
    if tok is None:
        raise ErroLogo(f"{cmd} requer um número")
    try:
        n = int(tok)
    except ValueError:
        raise ErroLogo(f"{cmd}: número inválido {tok!r}") from None
    if n < 0:
        raise ErroLogo(f"{cmd}: número negativo {n}")
    return n


def _bloco(toks: list[str], i: int) -> tuple[list[str], int]:
    """Extrai tokens entre [ ] (i aponta para o '[')."""
    if i >= len(toks) or toks[i] != "[":
        raise ErroLogo("REPEAT requer bloco entre colchetes")
    prof, j = 1, i + 1
    while j < len(toks) and prof:
        prof += (toks[j] == "[") - (toks[j] == "]")
        j += 1
    if prof:
        raise ErroLogo("'[' sem ']' correspondente")
    return toks[i + 1:j - 1], j


def _exec(toks: list[str], t: Tartaruga, limite: int) -> None:
    i = 0
    while i < len(toks):
        cmd = _ALIAS.get(toks[i], toks[i])
        i += 1
        t.passos += 1
        if t.passos > limite:
            raise ErroLogo("limite de comandos excedido")
        if cmd in ("FORWARD", "BACK"):
            n = _inteiro(toks[i] if i < len(toks) else None, cmd)
            i += 1
            t.mover(n, 1 if cmd == "FORWARD" else -1)
        elif cmd in ("LEFT", "RIGHT"):
            n = _inteiro(toks[i] if i < len(toks) else None, cmd)
            i += 1
            if n % 90:
                raise ErroLogo(f"{cmd}: apenas múltiplos de 90 graus (recebeu {n})")
            giro = n // 90 * (1 if cmd == "RIGHT" else -1)
            t.direcao = (t.direcao + giro) % 4
        elif cmd == "PENUP":
            t.caneta = False
        elif cmd == "PENDOWN":
            t.caneta = True
        elif cmd == "HOME":
            t.x = t.y = 0
        elif cmd == "REPEAT":
            n = _inteiro(toks[i] if i < len(toks) else None, cmd)
            corpo, i = _bloco(toks, i + 1)
            for _ in range(n):
                _exec(corpo, t, limite)
        else:
            raise ErroLogo(f"comando desconhecido: {cmd}")


def executar(fonte: str, limite: int = 100_000) -> Tartaruga:
    """Executa o programa e devolve o estado final da tartaruga."""
    t = Tartaruga()
    _exec(_tokens(fonte), t, limite)
    return t


def desenhar(t: Tartaruga) -> str:
    """Renderiza os pontos riscados como texto ('#'), com a tartaruga em '@'."""
    pts = t.riscados | {(t.x, t.y)}
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    linhas = []
    for y in range(max(ys), min(ys) - 1, -1):
        linhas.append("".join(
            "@" if (x, y) == (t.x, t.y) else "#" if (x, y) in t.riscados else "."
            for x in range(min(xs), max(xs) + 1)))
    return "\n".join(linhas)
