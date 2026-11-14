"""Visitor genérico e transformador para a AST de Mini.

``Visitante`` despacha para ``visitar_<Classe>`` e, na falta do método,
percorre os filhos. ``Transformador`` reconstrói a árvore (os nós originais
nunca são alterados): ``transformar_<Classe>`` pode devolver um nó, uma lista
de nós (emendada na lista pai) ou ``None`` (remove o item da lista; em campo
opcional vira ``None``).
"""
from __future__ import annotations

import dataclasses
from typing import Any, Iterator

from comp_ast import Chamada, No


def filhos(no: No) -> list[No]:
    """Filhos diretos de um nó, na ordem dos campos."""
    saida: list[No] = []
    for f in dataclasses.fields(no):
        v = getattr(no, f.name)
        if isinstance(v, No):
            saida.append(v)
        elif isinstance(v, list):
            saida.extend(x for x in v if isinstance(x, No))
    return saida


def percorrer(no: No) -> Iterator[No]:
    """Todos os nós da subárvore em pré-ordem (inclui o próprio)."""
    yield no
    for f in filhos(no):
        yield from percorrer(f)


def contem(no: No, *tipos: type) -> bool:
    return any(isinstance(n, tipos) for n in percorrer(no))


def eh_pura(expr: No) -> bool:
    """Expressão sem chamadas de função (logo, sem efeitos colaterais)."""
    return not contem(expr, Chamada)


class Visitante:
    def visitar(self, no: No) -> Any:
        metodo = getattr(self, "visitar_" + type(no).__name__, self.generico)
        return metodo(no)

    def generico(self, no: No) -> Any:
        for f in filhos(no):
            self.visitar(f)
        return None


class Transformador:
    def transformar(self, no: No) -> Any:
        metodo = getattr(self, "transformar_" + type(no).__name__, self.generico)
        return metodo(no)

    def generico(self, no: No) -> No:
        """Reconstrói o nó com os filhos transformados."""
        mudancas: dict[str, Any] = {}
        for f in dataclasses.fields(no):
            v = getattr(no, f.name)
            if isinstance(v, No):
                mudancas[f.name] = self.transformar(v)
            elif isinstance(v, list):
                nova: list[Any] = []
                for x in v:
                    if not isinstance(x, No):
                        nova.append(x)
                        continue
                    r = self.transformar(x)
                    if r is None:
                        continue
                    if isinstance(r, list):
                        nova.extend(r)
                    else:
                        nova.append(r)
                mudancas[f.name] = nova
        return dataclasses.replace(no, **mudancas)
