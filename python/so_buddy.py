"""Alocador buddy (companheiros binários).

Os pedidos são arredondados para a próxima potência de dois (>= bloco mínimo).
Um bloco maior é dividido até o tamanho certo; ao liberar, o bloco se funde com
seu companheiro (endereço XOR tamanho) enquanto este estiver livre.
"""
from __future__ import annotations


class SemMemoria(Exception):
    pass


def _potencia_de_dois(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


class Buddy:
    def __init__(self, total: int, minimo: int = 1) -> None:
        if not _potencia_de_dois(total) or not _potencia_de_dois(minimo) or minimo > total:
            raise ValueError("total e minimo devem ser potências de dois, minimo <= total")
        self.total = total
        self.minimo = minimo
        self.livres: dict[int, set[int]] = {total: {0}}  # tamanho -> endereços livres
        self.alocados: dict[int, tuple[int, int]] = {}  # endereço -> (tamanho, pedido)

    def _tamanho_para(self, pedido: int) -> int:
        tam = self.minimo
        while tam < pedido:
            tam *= 2
        return tam

    def alocar(self, pedido: int) -> int:
        if pedido <= 0:
            raise ValueError("pedido deve ser positivo")
        tam = self._tamanho_para(pedido)
        if tam > self.total:
            raise SemMemoria(f"pedido {pedido} excede a memória")
        origem = tam
        while origem <= self.total and not self.livres.get(origem):
            origem *= 2
        if origem > self.total:
            raise SemMemoria(f"sem bloco livre de {tam}")
        endereco = min(self.livres[origem])
        self.livres[origem].remove(endereco)
        while origem > tam:  # divide, devolvendo a metade de cima à lista
            origem //= 2
            self.livres.setdefault(origem, set()).add(endereco + origem)
        self.alocados[endereco] = (tam, pedido)
        return endereco

    def liberar(self, endereco: int) -> None:
        if endereco not in self.alocados:
            raise KeyError(endereco)
        tam, _ = self.alocados.pop(endereco)
        while tam < self.total:
            companheiro = endereco ^ tam
            lista = self.livres.get(tam, set())
            if companheiro not in lista:
                break
            lista.remove(companheiro)
            endereco = min(endereco, companheiro)
            tam *= 2
        self.livres.setdefault(tam, set()).add(endereco)

    def livre_total(self) -> int:
        return sum(tam * len(ends) for tam, ends in self.livres.items())

    def blocos_livres(self) -> list[tuple[int, int]]:
        """(endereço, tamanho) de todos os blocos livres, ordenado por endereço."""
        return sorted((e, tam) for tam, ends in self.livres.items() for e in ends)

    def fragmentacao_interna(self) -> int:
        return sum(tam - pedido for tam, pedido in self.alocados.values())
