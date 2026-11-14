"""LabelEncoder e OneHotEncoder com fit/transform."""
from __future__ import annotations


class LabelEncoder:
    def __init__(self) -> None:
        self.classes: list = []
        self._indice: dict = {}

    def ajustar(self, valores: list) -> "LabelEncoder":
        self.classes = sorted(set(valores), key=lambda v: (str(type(v)), v))
        self._indice = {c: i for i, c in enumerate(self.classes)}
        return self

    def transformar(self, valores: list) -> list[int]:
        try:
            return [self._indice[v] for v in valores]
        except KeyError as e:
            raise ValueError(f"categoria desconhecida: {e.args[0]!r}") from None

    def ajustar_transformar(self, valores: list) -> list[int]:
        return self.ajustar(valores).transformar(valores)

    def inverter(self, codigos: list[int]) -> list:
        if any(not 0 <= c < len(self.classes) for c in codigos):
            raise ValueError("código fora do intervalo")
        return [self.classes[c] for c in codigos]


class OneHotEncoder:
    def __init__(self, ignorar_desconhecidos: bool = False) -> None:
        self.ignorar_desconhecidos = ignorar_desconhecidos
        self.rotulos = LabelEncoder()

    @property
    def categorias(self) -> list:
        return self.rotulos.classes

    def ajustar(self, valores: list) -> "OneHotEncoder":
        self.rotulos.ajustar(valores)
        return self

    def transformar(self, valores: list) -> list[list[int]]:
        n = len(self.categorias)
        saida = []
        for v in valores:
            linha = [0] * n
            if v in self.rotulos._indice:
                linha[self.rotulos._indice[v]] = 1
            elif not self.ignorar_desconhecidos:
                raise ValueError(f"categoria desconhecida: {v!r}")
            saida.append(linha)
        return saida

    def ajustar_transformar(self, valores: list) -> list[list[int]]:
        return self.ajustar(valores).transformar(valores)

    def inverter(self, matriz: list[list[int]]) -> list:
        saida = []
        for linha in matriz:
            if sum(linha) != 1:
                raise ValueError("linha one-hot inválida")
            saida.append(self.categorias[linha.index(1)])
        return saida
