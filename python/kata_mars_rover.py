"""Mars Rover Kata: robô em grade esférica (wrap) com obstáculos."""
from __future__ import annotations

_DIRS = "NESW"
_DELTA = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}


class Rover:
    def __init__(self, x: int, y: int, direcao: str, largura: int = 10,
                 altura: int = 10, obstaculos: set[tuple[int, int]] | None = None) -> None:
        if direcao not in _DIRS:
            raise ValueError("direção inválida")
        self.x, self.y, self.direcao = x, y, direcao
        self.largura, self.altura = largura, altura
        self.obstaculos = obstaculos or set()

    def _mover(self, sentido: int) -> bool:
        dx, dy = _DELTA[self.direcao]
        nx = (self.x + sentido * dx) % self.largura
        ny = (self.y + sentido * dy) % self.altura
        if (nx, ny) in self.obstaculos:
            return False
        self.x, self.y = nx, ny
        return True

    def executar(self, comandos: str) -> str:
        """Executa comandos F, B, L, R. Ao bater em obstáculo para e prefixa 'O:'."""
        for c in comandos:
            if c == "L":
                self.direcao = _DIRS[(_DIRS.index(self.direcao) - 1) % 4]
            elif c == "R":
                self.direcao = _DIRS[(_DIRS.index(self.direcao) + 1) % 4]
            elif c in ("F", "B"):
                if not self._mover(1 if c == "F" else -1):
                    return "O:" + self.posicao()
            else:
                raise ValueError(f"comando inválido: {c}")
        return self.posicao()

    def posicao(self) -> str:
        return f"{self.x}:{self.y}:{self.direcao}"
