"""Trie com autocompletar ordenado por frequência e depois alfabeticamente."""

from __future__ import annotations


class _No:
    __slots__ = ("filhos", "freq")

    def __init__(self) -> None:
        self.filhos: dict[str, _No] = {}
        self.freq = 0  # > 0 marca fim de palavra


class Autocompletar:
    def __init__(self) -> None:
        self._raiz = _No()
        self._palavras = 0

    def __len__(self) -> int:
        return self._palavras

    def adicionar(self, palavra: str, peso: int = 1) -> None:
        if not palavra:
            raise ValueError("palavra vazia")
        if peso <= 0:
            raise ValueError("peso deve ser positivo")
        no = self._raiz
        for c in palavra:
            no = no.filhos.setdefault(c, _No())
        if no.freq == 0:
            self._palavras += 1
        no.freq += peso

    def contem(self, palavra: str) -> bool:
        no = self._buscar(palavra)
        return bool(no and no.freq)

    def _buscar(self, prefixo: str) -> _No | None:
        no = self._raiz
        for c in prefixo:
            no = no.filhos.get(c)
            if no is None:
                return None
        return no

    def sugerir(self, prefixo: str, limite: int = 5) -> list[str]:
        """Até `limite` palavras com o prefixo, mais frequentes primeiro."""
        if limite <= 0:
            return []
        no = self._buscar(prefixo)
        if no is None:
            return []
        achadas: list[tuple[int, str]] = []
        pilha = [(no, prefixo)]
        while pilha:
            n, p = pilha.pop()
            if n.freq:
                achadas.append((-n.freq, p))
            for c, f in n.filhos.items():
                pilha.append((f, p + c))
        achadas.sort()
        return [p for _, p in achadas[:limite]]
