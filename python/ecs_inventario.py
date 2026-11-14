"""Inventário com slots, empilhamento e limite de peso."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: str
    nome: str
    peso: float = 0.0
    max_pilha: int = 1


class Inventario:
    def __init__(self, slots: int, peso_max: float | None = None) -> None:
        if slots < 1:
            raise ValueError("slots deve ser >= 1")
        self.peso_max = peso_max
        self._slots: list[tuple[Item, int] | None] = [None] * slots

    @property
    def peso(self) -> float:
        return sum(i.peso * q for s in self._slots if s for i, q in [s])

    def contar(self, item_id: str) -> int:
        return sum(q for s in self._slots if s and s[0].id == item_id for q in [s[1]])

    def slot(self, indice: int) -> tuple[Item, int] | None:
        return self._slots[indice]

    def livres(self) -> int:
        return sum(1 for s in self._slots if s is None)

    def _cabe_por_peso(self, item: Item) -> int:
        if self.peso_max is None or item.peso <= 0:
            return 10 ** 9
        return max(0, int((self.peso_max - self.peso + 1e-9) // item.peso))

    def adicionar(self, item: Item, qtd: int = 1) -> int:
        """Adiciona até onde couber (slots e peso). Devolve a quantidade que NÃO coube."""
        if qtd < 0:
            raise ValueError("qtd não pode ser negativa")
        if item.max_pilha < 1:
            raise ValueError("max_pilha deve ser >= 1")
        permitido = min(qtd, self._cabe_por_peso(item))
        restante = permitido
        for i, s in enumerate(self._slots):  # completa pilhas existentes
            if restante == 0:
                break
            if s and s[0].id == item.id and s[1] < item.max_pilha:
                add = min(restante, item.max_pilha - s[1])
                self._slots[i] = (s[0], s[1] + add)
                restante -= add
        for i, s in enumerate(self._slots):  # abre pilhas novas
            if restante == 0:
                break
            if s is None:
                add = min(restante, item.max_pilha)
                self._slots[i] = (item, add)
                restante -= add
        return qtd - (permitido - restante)

    def remover(self, item_id: str, qtd: int = 1) -> None:
        """Remove `qtd` do item (das últimas pilhas para as primeiras); tudo ou nada."""
        if qtd < 0:
            raise ValueError("qtd não pode ser negativa")
        if self.contar(item_id) < qtd:
            raise ValueError(f"quantidade insuficiente de {item_id}")
        falta = qtd
        for i in range(len(self._slots) - 1, -1, -1):
            s = self._slots[i]
            if falta == 0:
                break
            if s and s[0].id == item_id:
                tirar = min(falta, s[1])
                falta -= tirar
                self._slots[i] = (s[0], s[1] - tirar) if s[1] > tirar else None

    def mover(self, origem: int, destino: int) -> None:
        """Move/troca/une pilhas entre slots."""
        a, b = self._slots[origem], self._slots[destino]
        if origem == destino or a is None:
            return
        if b is not None and b[0].id == a[0].id:
            total = a[1] + b[1]
            fica = min(total, a[0].max_pilha)
            self._slots[destino] = (b[0], fica)
            self._slots[origem] = (a[0], total - fica) if total > fica else None
        else:
            self._slots[origem], self._slots[destino] = b, a

    def dividir(self, indice: int, qtd: int) -> int:
        """Separa `qtd` unidades do slot para o primeiro slot livre; devolve o índice novo."""
        s = self._slots[indice]
        if s is None or not 0 < qtd < s[1]:
            raise ValueError("divisão inválida")
        for j, t in enumerate(self._slots):
            if t is None:
                self._slots[indice] = (s[0], s[1] - qtd)
                self._slots[j] = (s[0], qtd)
                return j
        raise ValueError("sem slot livre")

    def organizar(self) -> None:
        """Agrupa por id, funde pilhas e compacta os slots no início."""
        itens: dict[str, tuple[Item, int]] = {}
        for s in self._slots:
            if s:
                item, q = itens.get(s[0].id, (s[0], 0))
                itens[s[0].id] = (item, q + s[1])
        novos: list[tuple[Item, int] | None] = []
        for item_id in sorted(itens):
            item, q = itens[item_id]
            while q > 0:
                n = min(q, item.max_pilha)
                novos.append((item, n))
                q -= n
        self._slots = novos + [None] * (len(self._slots) - len(novos))


def transferir(origem: Inventario, destino: Inventario, item_id: str, qtd: int) -> int:
    """Move até `qtd` unidades; devolve quantas foram de fato transferidas."""
    modelo = next((s[0] for s in origem._slots if s and s[0].id == item_id), None)
    if modelo is None:
        return 0
    qtd = min(qtd, origem.contar(item_id))
    sobra = destino.adicionar(modelo, qtd)
    movido = qtd - sobra
    if movido:
        origem.remover(item_id, movido)
    return movido
