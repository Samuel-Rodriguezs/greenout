"""B-tree (Cormen) com grau mínimo t: inserção, busca e remoção."""
from __future__ import annotations

from typing import Any, Iterator, Optional


class No:
    def __init__(self, folha: bool) -> None:
        self.chaves: list[Any] = []
        self.valores: list[Any] = []
        self.filhos: list["No"] = []
        self.folha = folha


class BTree:
    def __init__(self, t: int = 2) -> None:
        if t < 2:
            raise ValueError("grau mínimo deve ser >= 2")
        self.t = t
        self.raiz = No(True)
        self.tamanho = 0

    def __len__(self) -> int:
        return self.tamanho

    def __contains__(self, chave: Any) -> bool:
        return self._localizar(chave) is not None

    @staticmethod
    def _pos(no: No, chave: Any) -> int:
        lo, hi = 0, len(no.chaves)
        while lo < hi:
            m = (lo + hi) // 2
            if no.chaves[m] < chave:
                lo = m + 1
            else:
                hi = m
        return lo

    def _localizar(self, chave: Any) -> Optional[tuple[No, int]]:
        no = self.raiz
        while True:
            i = self._pos(no, chave)
            if i < len(no.chaves) and no.chaves[i] == chave:
                return no, i
            if no.folha:
                return None
            no = no.filhos[i]

    def buscar(self, chave: Any) -> Optional[Any]:
        achado = self._localizar(chave)
        return None if achado is None else achado[0].valores[achado[1]]

    def _dividir(self, pai: No, i: int) -> None:
        t = self.t
        y = pai.filhos[i]
        z = No(y.folha)
        z.chaves = y.chaves[t:]
        z.valores = y.valores[t:]
        kc, kv = y.chaves[t - 1], y.valores[t - 1]
        y.chaves = y.chaves[: t - 1]
        y.valores = y.valores[: t - 1]
        if not y.folha:
            z.filhos = y.filhos[t:]
            y.filhos = y.filhos[:t]
        pai.filhos.insert(i + 1, z)
        pai.chaves.insert(i, kc)
        pai.valores.insert(i, kv)

    def inserir(self, chave: Any, valor: Any = None) -> None:
        """Insere; se a chave já existe, substitui o valor."""
        achado = self._localizar(chave)
        if achado is not None:
            achado[0].valores[achado[1]] = valor
            return
        if len(self.raiz.chaves) == 2 * self.t - 1:
            nova = No(False)
            nova.filhos.append(self.raiz)
            self.raiz = nova
            self._dividir(nova, 0)
        no = self.raiz
        while not no.folha:
            i = self._pos(no, chave)
            if len(no.filhos[i].chaves) == 2 * self.t - 1:
                self._dividir(no, i)
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]
        i = self._pos(no, chave)
        no.chaves.insert(i, chave)
        no.valores.insert(i, valor)
        self.tamanho += 1

    # ---- remoção ----
    def remover(self, chave: Any) -> bool:
        if self._localizar(chave) is None:
            return False
        self._remover(self.raiz, chave)
        if not self.raiz.chaves and not self.raiz.folha:
            self.raiz = self.raiz.filhos[0]
        self.tamanho -= 1
        return True

    def _remover(self, no: No, chave: Any) -> None:
        t = self.t
        i = self._pos(no, chave)
        achou = i < len(no.chaves) and no.chaves[i] == chave
        if no.folha:
            del no.chaves[i]
            del no.valores[i]
            return
        if achou:
            if len(no.filhos[i].chaves) >= t:
                pk, pv = self._maximo(no.filhos[i])
                no.chaves[i], no.valores[i] = pk, pv
                self._remover(no.filhos[i], pk)
            elif len(no.filhos[i + 1].chaves) >= t:
                sk, sv = self._minimo(no.filhos[i + 1])
                no.chaves[i], no.valores[i] = sk, sv
                self._remover(no.filhos[i + 1], sk)
            else:
                self._fundir(no, i)
                self._remover(no.filhos[i], chave)
            return
        if len(no.filhos[i].chaves) < t:
            i = self._garantir(no, i)
        self._remover(no.filhos[i], chave)

    def _garantir(self, no: No, i: int) -> int:
        t = self.t
        if i > 0 and len(no.filhos[i - 1].chaves) >= t:
            f, irmao = no.filhos[i], no.filhos[i - 1]
            f.chaves.insert(0, no.chaves[i - 1])
            f.valores.insert(0, no.valores[i - 1])
            no.chaves[i - 1] = irmao.chaves.pop()
            no.valores[i - 1] = irmao.valores.pop()
            if not irmao.folha:
                f.filhos.insert(0, irmao.filhos.pop())
            return i
        if i < len(no.filhos) - 1 and len(no.filhos[i + 1].chaves) >= t:
            f, irmao = no.filhos[i], no.filhos[i + 1]
            f.chaves.append(no.chaves[i])
            f.valores.append(no.valores[i])
            no.chaves[i] = irmao.chaves.pop(0)
            no.valores[i] = irmao.valores.pop(0)
            if not irmao.folha:
                f.filhos.append(irmao.filhos.pop(0))
            return i
        if i == len(no.filhos) - 1:
            i -= 1
        self._fundir(no, i)
        return i

    def _fundir(self, no: No, i: int) -> None:
        a, b = no.filhos[i], no.filhos[i + 1]
        a.chaves.append(no.chaves.pop(i))
        a.valores.append(no.valores.pop(i))
        a.chaves += b.chaves
        a.valores += b.valores
        a.filhos += b.filhos
        del no.filhos[i + 1]

    @staticmethod
    def _maximo(no: No) -> tuple[Any, Any]:
        while not no.folha:
            no = no.filhos[-1]
        return no.chaves[-1], no.valores[-1]

    @staticmethod
    def _minimo(no: No) -> tuple[Any, Any]:
        while not no.folha:
            no = no.filhos[0]
        return no.chaves[0], no.valores[0]

    def itens(self) -> Iterator[tuple[Any, Any]]:
        def rec(no: No) -> Iterator[tuple[Any, Any]]:
            for i, k in enumerate(no.chaves):
                if not no.folha:
                    yield from rec(no.filhos[i])
                yield k, no.valores[i]
            if not no.folha:
                yield from rec(no.filhos[-1])
        return rec(self.raiz)

    def altura(self) -> int:
        h, no = 1, self.raiz
        while not no.folha:
            h += 1
            no = no.filhos[0]
        return h

    def validar(self) -> bool:
        """Verifica invariantes: ocupação, ordem e altura uniforme."""
        t = self.t
        profs: set[int] = set()

        def rec(no: No, prof: int, lo: Any, hi: Any, raiz: bool) -> None:
            n = len(no.chaves)
            if n > 2 * t - 1 or (not raiz and n < t - 1):
                raise AssertionError("ocupação inválida")
            if no.chaves != sorted(no.chaves):
                raise AssertionError("chaves fora de ordem")
            for k in no.chaves:
                if (lo is not None and k <= lo) or (hi is not None and k >= hi):
                    raise AssertionError("chave fora do intervalo")
            if no.folha:
                profs.add(prof)
                return
            if len(no.filhos) != n + 1:
                raise AssertionError("número de filhos inválido")
            limites = [lo] + no.chaves + [hi]
            for j, f in enumerate(no.filhos):
                rec(f, prof + 1, limites[j], limites[j + 1], False)

        rec(self.raiz, 0, None, None, True)
        return len(profs) == 1
