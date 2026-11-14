"""Geração de texto por cadeia de Markov de palavras (reprodutível com seed)."""
import random
from collections import defaultdict


class CadeiaMarkov:
    def __init__(self, ordem: int = 1) -> None:
        if ordem < 1:
            raise ValueError("ordem deve ser >= 1")
        self.ordem = ordem
        self.transicoes: dict[tuple[str, ...], list[str]] = defaultdict(list)

    def treinar(self, texto: str) -> "CadeiaMarkov":
        palavras = texto.split()
        for i in range(len(palavras) - self.ordem):
            estado = tuple(palavras[i:i + self.ordem])
            self.transicoes[estado].append(palavras[i + self.ordem])
        return self

    def gerar(self, n_palavras: int, seed: int | None = None) -> str:
        if n_palavras < 0:
            raise ValueError("n_palavras deve ser >= 0")
        if not self.transicoes:
            raise ValueError("texto de treino insuficiente")
        rng = random.Random(seed)
        estados = list(self.transicoes)
        estado = rng.choice(estados)
        saida = list(estado)
        while len(saida) < n_palavras:
            if estado in self.transicoes:
                proxima = rng.choice(self.transicoes[estado])
                saida.append(proxima)
                estado = estado[1:] + (proxima,)
            else:  # beco sem saída: recomeça de um estado aleatório
                estado = rng.choice(estados)
                saida.extend(estado)
        return " ".join(saida[:n_palavras])
