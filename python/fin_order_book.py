"""Livro de ofertas com casamento por prioridade preço-tempo."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ordem:
    id: int
    lado: str  # "compra" ou "venda"
    preco: float
    quantidade: float


@dataclass(frozen=True)
class Negocio:
    preco: float
    quantidade: float
    id_compra: int
    id_venda: int


class LivroOfertas:
    def __init__(self) -> None:
        self._compras: list[Ordem] = []  # maior preço primeiro, depois mais antiga
        self._vendas: list[Ordem] = []  # menor preço primeiro, depois mais antiga
        self._proximo_id = 1

    def enviar(
        self, lado: str, quantidade: float, preco: float | None = None
    ) -> tuple[int, list[Negocio]]:
        """Envia ordem limite (preco informado) ou a mercado (preco=None).
        Devolve (id, negócios). O saldo de ordem limite fica no livro; o de
        ordem a mercado é descartado."""
        if lado not in ("compra", "venda"):
            raise ValueError("lado deve ser 'compra' ou 'venda'")
        if quantidade <= 0:
            raise ValueError("quantidade deve ser positiva")
        if preco is not None and preco <= 0:
            raise ValueError("preço deve ser positivo")
        ordem = Ordem(self._proximo_id, lado, preco if preco is not None else 0.0, quantidade)
        self._proximo_id += 1
        contra = self._vendas if lado == "compra" else self._compras
        negocios: list[Negocio] = []
        while ordem.quantidade > 0 and contra:
            melhor = contra[0]
            if preco is not None:
                if lado == "compra" and melhor.preco > preco:
                    break
                if lado == "venda" and melhor.preco < preco:
                    break
            q = min(ordem.quantidade, melhor.quantidade)
            ids = (ordem.id, melhor.id) if lado == "compra" else (melhor.id, ordem.id)
            negocios.append(Negocio(melhor.preco, q, ids[0], ids[1]))
            ordem.quantidade -= q
            melhor.quantidade -= q
            if melhor.quantidade == 0:
                contra.pop(0)
        if ordem.quantidade > 0 and preco is not None:
            self._inserir(ordem)
        return ordem.id, negocios

    def _inserir(self, ordem: Ordem) -> None:
        lista = self._compras if ordem.lado == "compra" else self._vendas
        sinal = -1 if ordem.lado == "compra" else 1
        pos = len(lista)
        for i, o in enumerate(lista):
            if sinal * ordem.preco < sinal * o.preco:
                pos = i
                break
        lista.insert(pos, ordem)

    def cancelar(self, id_ordem: int) -> bool:
        for lista in (self._compras, self._vendas):
            for i, o in enumerate(lista):
                if o.id == id_ordem:
                    del lista[i]
                    return True
        return False

    def melhor_compra(self) -> float | None:
        return self._compras[0].preco if self._compras else None

    def melhor_venda(self) -> float | None:
        return self._vendas[0].preco if self._vendas else None

    def spread(self) -> float | None:
        if not self._compras or not self._vendas:
            return None
        return self._vendas[0].preco - self._compras[0].preco

    def profundidade(self, lado: str) -> list[tuple[float, float]]:
        """Pares (preço, quantidade total) agregados por nível de preço."""
        if lado not in ("compra", "venda"):
            raise ValueError("lado deve ser 'compra' ou 'venda'")
        niveis: dict[float, float] = {}
        for o in self._compras if lado == "compra" else self._vendas:
            niveis[o.preco] = niveis.get(o.preco, 0.0) + o.quantidade
        return list(niveis.items())
