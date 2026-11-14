"""Árvore AVL (conjunto ordenado) com inserção e remoção balanceadas."""

from __future__ import annotations

from typing import Iterator, Optional


class No:
    def __init__(self, chave: int) -> None:
        self.chave = chave
        self.esq: Optional[No] = None
        self.dir: Optional[No] = None
        self.altura = 1


def _alt(n: Optional[No]) -> int:
    return n.altura if n else 0


def _atualiza(n: No) -> None:
    n.altura = 1 + max(_alt(n.esq), _alt(n.dir))


def _fator(n: No) -> int:
    return _alt(n.esq) - _alt(n.dir)


def _rot_dir(y: No) -> No:
    x = y.esq
    y.esq, x.dir = x.dir, y
    _atualiza(y)
    _atualiza(x)
    return x


def _rot_esq(x: No) -> No:
    y = x.dir
    x.dir, y.esq = y.esq, x
    _atualiza(x)
    _atualiza(y)
    return y


def _balancear(n: No) -> No:
    _atualiza(n)
    f = _fator(n)
    if f > 1:
        if _fator(n.esq) < 0:
            n.esq = _rot_esq(n.esq)
        return _rot_dir(n)
    if f < -1:
        if _fator(n.dir) > 0:
            n.dir = _rot_dir(n.dir)
        return _rot_esq(n)
    return n


class ArvoreAVL:
    def __init__(self) -> None:
        self.raiz: Optional[No] = None
        self._tam = 0

    def __len__(self) -> int:
        return self._tam

    def __contains__(self, chave: int) -> bool:
        n = self.raiz
        while n:
            if chave == n.chave:
                return True
            n = n.esq if chave < n.chave else n.dir
        return False

    def inserir(self, chave: int) -> bool:
        """Insere; retorna False se já existia."""
        antes = self._tam

        def ins(n: Optional[No]) -> No:
            if n is None:
                self._tam += 1
                return No(chave)
            if chave < n.chave:
                n.esq = ins(n.esq)
            elif chave > n.chave:
                n.dir = ins(n.dir)
            else:
                return n
            return _balancear(n)

        self.raiz = ins(self.raiz)
        return self._tam > antes

    def remover(self, chave: int) -> bool:
        antes = self._tam

        def rem(n: Optional[No], c: int) -> Optional[No]:
            if n is None:
                return None
            if c < n.chave:
                n.esq = rem(n.esq, c)
            elif c > n.chave:
                n.dir = rem(n.dir, c)
            else:
                if n.esq is None or n.dir is None:
                    self._tam -= 1
                    return n.esq or n.dir
                suc = n.dir
                while suc.esq:
                    suc = suc.esq
                n.chave = suc.chave
                n.dir = rem(n.dir, suc.chave)
            return _balancear(n)

        self.raiz = rem(self.raiz, chave)
        return self._tam < antes

    def altura(self) -> int:
        return _alt(self.raiz)

    def __iter__(self) -> Iterator[int]:
        pilha: list[No] = []
        n = self.raiz
        while pilha or n:
            while n:
                pilha.append(n)
                n = n.esq
            n = pilha.pop()
            yield n.chave
            n = n.dir

    def balanceada(self) -> bool:
        def ok(n: Optional[No]) -> bool:
            return n is None or (abs(_fator(n)) <= 1 and ok(n.esq) and ok(n.dir))

        return ok(self.raiz)
