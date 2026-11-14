"""B+tree: dados só nas folhas, folhas encadeadas, varredura de intervalo."""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from typing import Any, Iterator, Optional


class Folha:
    def __init__(self) -> None:
        self.chaves: list[Any] = []
        self.valores: list[Any] = []
        self.proxima: Optional["Folha"] = None


class Interno:
    def __init__(self) -> None:
        self.chaves: list[Any] = []
        self.filhos: list[Any] = []


class BMais:
    def __init__(self, ordem: int = 4) -> None:
        if ordem < 3:
            raise ValueError("ordem deve ser >= 3")
        self.ordem = ordem  # máximo de filhos / máximo de chaves por folha = ordem - 1
        self.raiz: Any = Folha()
        self.tamanho = 0

    def __len__(self) -> int:
        return self.tamanho

    def _descer(self, chave: Any) -> tuple[Folha, list[tuple[Interno, int]]]:
        caminho: list[tuple[Interno, int]] = []
        no = self.raiz
        while isinstance(no, Interno):
            i = bisect_right(no.chaves, chave)
            caminho.append((no, i))
            no = no.filhos[i]
        return no, caminho

    def buscar(self, chave: Any) -> Optional[Any]:
        folha, _ = self._descer(chave)
        i = bisect_left(folha.chaves, chave)
        if i < len(folha.chaves) and folha.chaves[i] == chave:
            return folha.valores[i]
        return None

    def inserir(self, chave: Any, valor: Any = None) -> None:
        folha, caminho = self._descer(chave)
        i = bisect_left(folha.chaves, chave)
        if i < len(folha.chaves) and folha.chaves[i] == chave:
            folha.valores[i] = valor
            return
        folha.chaves.insert(i, chave)
        folha.valores.insert(i, valor)
        self.tamanho += 1
        if len(folha.chaves) < self.ordem:
            return
        meio = len(folha.chaves) // 2
        nova = Folha()
        nova.chaves = folha.chaves[meio:]
        nova.valores = folha.valores[meio:]
        folha.chaves = folha.chaves[:meio]
        folha.valores = folha.valores[:meio]
        nova.proxima = folha.proxima
        folha.proxima = nova
        self._propagar(caminho, nova.chaves[0], nova)

    def _propagar(self, caminho: list[tuple[Interno, int]], chave: Any, novo: Any) -> None:
        while caminho:
            pai, i = caminho.pop()
            pai.chaves.insert(i, chave)
            pai.filhos.insert(i + 1, novo)
            if len(pai.filhos) <= self.ordem:
                return
            meio = len(pai.chaves) // 2
            chave = pai.chaves[meio]
            irmao = Interno()
            irmao.chaves = pai.chaves[meio + 1:]
            irmao.filhos = pai.filhos[meio + 1:]
            pai.chaves = pai.chaves[:meio]
            pai.filhos = pai.filhos[: meio + 1]
            novo = irmao
        raiz = Interno()
        raiz.chaves = [chave]
        raiz.filhos = [self.raiz, novo]
        self.raiz = raiz

    def remover(self, chave: Any) -> bool:
        """Remove da folha. Nós podem ficar com ocupação baixa, mas a árvore
        continua correta (remoção preguiçosa); folhas vazias são desligadas."""
        folha, caminho = self._descer(chave)
        i = bisect_left(folha.chaves, chave)
        if i >= len(folha.chaves) or folha.chaves[i] != chave:
            return False
        del folha.chaves[i]
        del folha.valores[i]
        self.tamanho -= 1
        if not folha.chaves and caminho:
            self._desligar(folha, caminho)
        return True

    def _desligar(self, folha: Folha, caminho: list[tuple[Interno, int]]) -> None:
        pai, i = caminho[-1]
        if len(pai.filhos) == 1:
            return  # mantém a folha vazia: a estrutura permanece consistente
        # ajusta encadeamento
        if i > 0:
            anterior = pai.filhos[i - 1]
            while isinstance(anterior, Interno):
                anterior = anterior.filhos[-1]
            anterior.proxima = folha.proxima
        else:
            ant = self._folha_anterior(folha)
            if ant is not None:
                ant.proxima = folha.proxima
        del pai.filhos[i]
        del pai.chaves[i - 1 if i > 0 else 0]
        if len(pai.filhos) == 1 and pai is self.raiz:
            self.raiz = pai.filhos[0]

    def _folha_anterior(self, alvo: Folha) -> Optional[Folha]:
        f = self._primeira()
        if f is alvo:
            return None
        while f is not None and f.proxima is not alvo:
            f = f.proxima
        return f

    def _primeira(self) -> Folha:
        no = self.raiz
        while isinstance(no, Interno):
            no = no.filhos[0]
        return no

    def itens(self) -> Iterator[tuple[Any, Any]]:
        f: Optional[Folha] = self._primeira()
        while f is not None:
            yield from zip(f.chaves, f.valores)
            f = f.proxima

    def intervalo(self, lo: Any = None, hi: Any = None, incluir_hi: bool = True) -> Iterator[tuple[Any, Any]]:
        """Itera pares com lo <= chave <= hi (hi exclusivo se incluir_hi=False)."""
        if lo is None:
            f: Optional[Folha] = self._primeira()
            i = 0
        else:
            f, _ = self._descer(lo)
            i = bisect_left(f.chaves, lo)
        while f is not None:
            while i < len(f.chaves):
                k = f.chaves[i]
                if hi is not None and (k > hi or (k == hi and not incluir_hi)):
                    return
                yield k, f.valores[i]
                i += 1
            f, i = f.proxima, 0

    def altura(self) -> int:
        h, no = 1, self.raiz
        while isinstance(no, Interno):
            h += 1
            no = no.filhos[0]
        return h
