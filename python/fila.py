from collections import deque


class Fila:
    def __init__(self):
        self._itens = deque()

    def enfileirar(self, x):
        self._itens.append(x)

    def desenfileirar(self):
        if not self._itens:
            raise IndexError("fila vazia")
        return self._itens.popleft()

    def __len__(self):
        return len(self._itens)
