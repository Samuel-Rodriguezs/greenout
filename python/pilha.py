class Pilha:
    def __init__(self):
        self._itens = []

    def empilhar(self, x):
        self._itens.append(x)

    def desempilhar(self):
        if not self._itens:
            raise IndexError("pilha vazia")
        return self._itens.pop()

    def topo(self):
        if not self._itens:
            raise IndexError("pilha vazia")
        return self._itens[-1]

    def __len__(self):
        return len(self._itens)


def parenteses_balanceados(texto: str) -> bool:
    pares = {")": "(", "]": "[", "}": "{"}
    p = Pilha()
    for ch in texto:
        if ch in "([{":
            p.empilhar(ch)
        elif ch in pares:
            if len(p) == 0 or p.desempilhar() != pares[ch]:
                return False
    return len(p) == 0
