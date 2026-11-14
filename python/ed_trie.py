"""Trie (árvore de prefixos) para strings."""
from __future__ import annotations

from typing import Dict, List


class _No:
    def __init__(self) -> None:
        self.filhos: Dict[str, "_No"] = {}
        self.fim = False


class Trie:
    def __init__(self) -> None:
        self._raiz = _No()
        self._tamanho = 0

    def __len__(self) -> int:
        return self._tamanho

    def inserir(self, palavra: str) -> bool:
        """Insere a palavra; retorna False se já existia."""
        no = self._raiz
        for c in palavra:
            no = no.filhos.setdefault(c, _No())
        if no.fim:
            return False
        no.fim = True
        self._tamanho += 1
        return True

    def _achar(self, prefixo: str) -> "_No | None":
        no = self._raiz
        for c in prefixo:
            no = no.filhos.get(c)
            if no is None:
                return None
        return no

    def contem(self, palavra: str) -> bool:
        no = self._achar(palavra)
        return no is not None and no.fim

    def tem_prefixo(self, prefixo: str) -> bool:
        return self._achar(prefixo) is not None

    def com_prefixo(self, prefixo: str) -> List[str]:
        """Palavras iniciadas por prefixo, em ordem alfabética."""
        no = self._achar(prefixo)
        resultado: List[str] = []
        if no is None:
            return resultado

        def coletar(atual: _No, acumulado: str) -> None:
            if atual.fim:
                resultado.append(acumulado)
            for c in sorted(atual.filhos):
                coletar(atual.filhos[c], acumulado + c)

        coletar(no, prefixo)
        return resultado

    def remover(self, palavra: str) -> None:
        """Remove a palavra; KeyError se ausente."""
        if not self.contem(palavra):
            raise KeyError(palavra)
        caminho = [self._raiz]
        for c in palavra:
            caminho.append(caminho[-1].filhos[c])
        caminho[-1].fim = False
        self._tamanho -= 1
        for i in range(len(palavra), 0, -1):
            no = caminho[i]
            if no.fim or no.filhos:
                break
            del caminho[i - 1].filhos[palavra[i - 1]]
