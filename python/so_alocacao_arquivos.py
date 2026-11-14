"""Métodos de alocação de arquivos em disco: contígua, encadeada e FAT.

Todos expõem a mesma interface; `leituras_ate(nome, i)` informa quantas
leituras de disco são necessárias para alcançar o bloco lógico `i`, que é o
critério clássico de comparação entre os métodos.
"""
from __future__ import annotations

from typing import Optional

FIM = -1


class SemEspaco(Exception):
    pass


class Alocacao:
    def __init__(self, nblocos: int) -> None:
        if nblocos <= 0:
            raise ValueError("nblocos deve ser positivo")
        self.nblocos = nblocos
        self.diretorio: dict[str, tuple[int, int]] = {}  # nome -> (primeiro bloco, tamanho)

    def _checar_novo(self, nome: str, n: int) -> None:
        if n <= 0:
            raise ValueError("número de blocos deve ser positivo")
        if nome in self.diretorio:
            raise ValueError(f"arquivo já existe: {nome}")

    def _checar_existe(self, nome: str) -> None:
        if nome not in self.diretorio:
            raise KeyError(nome)

    def livres(self) -> list[int]:
        raise NotImplementedError

    def criar(self, nome: str, n: int) -> list[int]:
        raise NotImplementedError

    def estender(self, nome: str, extra: int) -> list[int]:
        raise NotImplementedError

    def remover(self, nome: str) -> None:
        raise NotImplementedError

    def blocos(self, nome: str) -> list[int]:
        raise NotImplementedError

    def leituras_ate(self, nome: str, i: int) -> int:
        raise NotImplementedError


class Contigua(Alocacao):
    """Cada arquivo ocupa uma sequência contínua (first fit)."""

    def __init__(self, nblocos: int) -> None:
        super().__init__(nblocos)
        self.usado = [False] * nblocos

    def livres(self) -> list[int]:
        return [i for i, u in enumerate(self.usado) if not u]

    def _achar(self, n: int) -> Optional[int]:
        corrida = 0
        for i, u in enumerate(self.usado):
            corrida = 0 if u else corrida + 1
            if corrida == n:
                return i - n + 1
        return None

    def criar(self, nome: str, n: int) -> list[int]:
        self._checar_novo(nome, n)
        inicio = self._achar(n)
        if inicio is None:
            raise SemEspaco(f"sem {n} blocos contíguos ({len(self.livres())} livres no total)")
        for b in range(inicio, inicio + n):
            self.usado[b] = True
        self.diretorio[nome] = (inicio, n)
        return list(range(inicio, inicio + n))

    def estender(self, nome: str, extra: int) -> list[int]:
        self._checar_existe(nome)
        inicio, n = self.diretorio[nome]
        novos = range(inicio + n, inicio + n + extra)
        if novos.stop > self.nblocos or any(self.usado[b] for b in novos):
            raise SemEspaco("bloco seguinte ocupado: seria preciso realocar o arquivo")
        for b in novos:
            self.usado[b] = True
        self.diretorio[nome] = (inicio, n + extra)
        return list(novos)

    def remover(self, nome: str) -> None:
        self._checar_existe(nome)
        inicio, n = self.diretorio.pop(nome)
        for b in range(inicio, inicio + n):
            self.usado[b] = False

    def blocos(self, nome: str) -> list[int]:
        self._checar_existe(nome)
        inicio, n = self.diretorio[nome]
        return list(range(inicio, inicio + n))

    def leituras_ate(self, nome: str, i: int) -> int:
        self._checar_existe(nome)
        if not 0 <= i < self.diretorio[nome][1]:
            raise IndexError(i)
        return 1  # acesso direto: base + i


class Encadeada(Alocacao):
    """Cada bloco guarda o ponteiro para o próximo; o diretório guarda o primeiro."""

    def __init__(self, nblocos: int) -> None:
        super().__init__(nblocos)
        self.proximo: list[Optional[int]] = [None] * nblocos  # None = livre
        self.ultimo: dict[str, int] = {}

    def livres(self) -> list[int]:
        return [i for i, p in enumerate(self.proximo) if p is None]

    def _pegar(self, n: int) -> list[int]:
        livres = self.livres()
        if len(livres) < n:
            raise SemEspaco(f"só {len(livres)} blocos livres")
        return livres[:n]

    def _ligar(self, escolhidos: list[int], anterior: Optional[int]) -> None:
        if anterior is not None:
            self.proximo[anterior] = escolhidos[0]
        for a, b in zip(escolhidos, escolhidos[1:]):
            self.proximo[a] = b
        self.proximo[escolhidos[-1]] = FIM

    def criar(self, nome: str, n: int) -> list[int]:
        self._checar_novo(nome, n)
        escolhidos = self._pegar(n)
        self._ligar(escolhidos, None)
        self.diretorio[nome] = (escolhidos[0], n)
        self.ultimo[nome] = escolhidos[-1]
        return escolhidos

    def estender(self, nome: str, extra: int) -> list[int]:
        self._checar_existe(nome)
        escolhidos = self._pegar(extra)
        self._ligar(escolhidos, self.ultimo[nome])
        primeiro, n = self.diretorio[nome]
        self.diretorio[nome] = (primeiro, n + extra)
        self.ultimo[nome] = escolhidos[-1]
        return escolhidos

    def blocos(self, nome: str) -> list[int]:
        self._checar_existe(nome)
        cadeia = []
        atual: Optional[int] = self.diretorio[nome][0]
        while atual != FIM:
            assert atual is not None
            cadeia.append(atual)
            atual = self.proximo[atual]
        return cadeia

    def remover(self, nome: str) -> None:
        for b in self.blocos(nome):
            self.proximo[b] = None
        del self.diretorio[nome]
        del self.ultimo[nome]

    def leituras_ate(self, nome: str, i: int) -> int:
        self._checar_existe(nome)
        if not 0 <= i < self.diretorio[nome][1]:
            raise IndexError(i)
        return i + 1  # percorre i ponteiros e lê o bloco


class FAT(Encadeada):
    """Mesma cadeia, mas os ponteiros ficam numa tabela (FAT) mantida em memória."""

    def leituras_ate(self, nome: str, i: int) -> int:
        self._checar_existe(nome)
        if not 0 <= i < self.diretorio[nome][1]:
            raise IndexError(i)
        return 1  # a travessia usa a FAT em RAM; só o bloco de dados vai ao disco

    @property
    def tabela(self) -> list[Optional[int]]:
        return self.proximo
