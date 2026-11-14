"""Tilemap com camadas nomeadas, conversão mundo/tile e janela visível."""
from __future__ import annotations


class Tilemap:
    VAZIO = 0

    def __init__(self, largura: int, altura: int, tamanho_tile: int = 16) -> None:
        if largura < 1 or altura < 1 or tamanho_tile < 1:
            raise ValueError("dimensões devem ser positivas")
        self.largura = largura
        self.altura = altura
        self.tamanho_tile = tamanho_tile
        self._camadas: dict[str, list[list[int]]] = {}
        self._ordem: list[str] = []
        self._solidos: set[int] = set()

    # camadas ---------------------------------------------------------
    def adicionar_camada(self, nome: str, preenchimento: int = 0) -> None:
        if nome in self._camadas:
            raise ValueError(f"camada já existe: {nome}")
        self._camadas[nome] = [[preenchimento] * self.largura for _ in range(self.altura)]
        self._ordem.append(nome)  # a última desenha por cima

    def camadas(self) -> list[str]:
        return list(self._ordem)

    def dentro(self, x: int, y: int) -> bool:
        return 0 <= x < self.largura and 0 <= y < self.altura

    def obter(self, camada: str, x: int, y: int) -> int:
        if not self.dentro(x, y):
            raise IndexError((x, y))
        return self._camadas[camada][y][x]

    def definir(self, camada: str, x: int, y: int, tile: int) -> None:
        if not self.dentro(x, y):
            raise IndexError((x, y))
        self._camadas[camada][y][x] = tile

    def preencher_retangulo(self, camada: str, x: int, y: int, w: int, h: int, tile: int) -> None:
        for j in range(max(0, y), min(self.altura, y + h)):
            for i in range(max(0, x), min(self.largura, x + w)):
                self._camadas[camada][j][i] = tile

    def tile_visivel(self, x: int, y: int) -> int:
        """Tile da camada mais alta não vazia (ou VAZIO)."""
        for nome in reversed(self._ordem):
            t = self.obter(nome, x, y)
            if t != self.VAZIO:
                return t
        return self.VAZIO

    # colisão ---------------------------------------------------------
    def definir_solidos(self, tiles: set[int]) -> None:
        self._solidos = set(tiles)

    def solido(self, x: int, y: int) -> bool:
        """Fora do mapa é sólido; senão, qualquer camada com tile sólido bloqueia."""
        if not self.dentro(x, y):
            return True
        return any(self._camadas[n][y][x] in self._solidos for n in self._ordem)

    # coordenadas -----------------------------------------------------
    def mundo_para_tile(self, px: float, py: float) -> tuple[int, int]:
        t = self.tamanho_tile
        return (int(px // t), int(py // t))

    def tile_para_mundo(self, x: int, y: int) -> tuple[int, int]:
        """Canto superior esquerdo do tile em pixels."""
        return (x * self.tamanho_tile, y * self.tamanho_tile)

    def janela(self, px: float, py: float, largura_px: float, altura_px: float) -> tuple[int, int, int, int]:
        """Intervalo de tiles visíveis (x0, y0, x1, y1), x1/y1 exclusivos, limitado ao mapa."""
        t = self.tamanho_tile
        x0 = min(self.largura, max(0, int(px // t)))
        y0 = min(self.altura, max(0, int(py // t)))
        x1 = min(self.largura, int(-((-(px + largura_px)) // t)))
        y1 = min(self.altura, int(-((-(py + altura_px)) // t)))
        return (x0, y0, max(x0, x1), max(y0, y1))
