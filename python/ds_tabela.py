"""Mini-DataFrame: Tabela com select/filtrar/ordenar/agrupar/join/pivot."""
from __future__ import annotations

import statistics
from typing import Any, Callable, Iterable

Linha = dict[str, Any]


def _soma(v: list[Any]) -> Any:
    return sum(v) if v else 0


def _media(v: list[Any]) -> Any:
    return sum(v) / len(v) if v else None


def _vazio_ou(f: Callable[[list[Any]], Any]) -> Callable[[list[Any]], Any]:
    return lambda v: f(v) if v else None


_AGREGADORES: dict[str, Callable[[list[Any]], Any]] = {
    "soma": _soma,
    "media": _media,
    "contagem": len,
    "min": _vazio_ou(min),
    "max": _vazio_ou(max),
    "mediana": _vazio_ou(statistics.median),
}


def _agregador(f: str | Callable[[list[Any]], Any]) -> Callable[[list[Any]], Any]:
    if callable(f):
        return f
    if f not in _AGREGADORES:
        raise ValueError(f"agregação desconhecida: {f}")
    return _AGREGADORES[f]


class Tabela:
    """Tabela imutável de linhas (dicionários) com colunas ordenadas."""

    def __init__(self, linhas: Iterable[Linha], colunas: list[str] | None = None) -> None:
        self._linhas: list[Linha] = [dict(l) for l in linhas]
        if colunas is None:
            colunas = []
            for l in self._linhas:
                for c in l:
                    if c not in colunas:
                        colunas.append(c)
        self.colunas: list[str] = list(colunas)
        for l in self._linhas:
            for c in self.colunas:
                l.setdefault(c, None)

    def __len__(self) -> int:
        return len(self._linhas)

    def linhas(self) -> list[Linha]:
        return [dict(l) for l in self._linhas]

    def coluna(self, nome: str) -> list[Any]:
        if nome not in self.colunas:
            raise KeyError(nome)
        return [l[nome] for l in self._linhas]

    def head(self, n: int = 5) -> "Tabela":
        return Tabela(self._linhas[:n], self.colunas)

    def select(self, *nomes: str) -> "Tabela":
        for n in nomes:
            if n not in self.colunas:
                raise KeyError(n)
        return Tabela([{n: l[n] for n in nomes} for l in self._linhas], list(nomes))

    def filtrar(self, predicado: Callable[[Linha], bool]) -> "Tabela":
        return Tabela([l for l in self._linhas if predicado(l)], self.colunas)

    def adicionar_coluna(self, nome: str, f: Callable[[Linha], Any]) -> "Tabela":
        novas = [{**l, nome: f(l)} for l in self._linhas]
        cols = self.colunas if nome in self.colunas else self.colunas + [nome]
        return Tabela(novas, cols)

    def ordenar(self, por: str | list[str], reverso: bool = False) -> "Tabela":
        chaves = [por] if isinstance(por, str) else list(por)
        linhas = list(self._linhas)
        for c in reversed(chaves):
            com = [l for l in linhas if l[c] is not None]
            sem = [l for l in linhas if l[c] is None]
            com.sort(key=lambda l: l[c], reverse=reverso)
            linhas = com + sem
        return Tabela(linhas, self.colunas)

    def agrupar(self, por: str | list[str], agregacoes: dict[str, tuple[str, str | Callable]]) -> "Tabela":
        """agregacoes: {nome_saida: (coluna, 'soma'|'media'|...|callable)}."""
        chaves = [por] if isinstance(por, str) else list(por)
        grupos: dict[tuple, list[Linha]] = {}
        for l in self._linhas:
            grupos.setdefault(tuple(l[c] for c in chaves), []).append(l)
        saida: list[Linha] = []
        for chave, membros in grupos.items():
            r: Linha = dict(zip(chaves, chave))
            for nome, (col, f) in agregacoes.items():
                valores = [m[col] for m in membros if m[col] is not None]
                r[nome] = _agregador(f)(valores)
            saida.append(r)
        return Tabela(saida, chaves + list(agregacoes))

    def join(self, outra: "Tabela", on: str | list[str], how: str = "inner") -> "Tabela":
        if how not in ("inner", "left"):
            raise ValueError("how deve ser 'inner' ou 'left'")
        chaves = [on] if isinstance(on, str) else list(on)
        extras = [c for c in outra.colunas if c not in chaves]
        nomes = {c: (c + "_dir" if c in self.colunas else c) for c in extras}
        indice: dict[tuple, list[Linha]] = {}
        for l in outra._linhas:
            indice.setdefault(tuple(l[c] for c in chaves), []).append(l)
        saida: list[Linha] = []
        for l in self._linhas:
            achados = indice.get(tuple(l[c] for c in chaves), [])
            if not achados and how == "left":
                saida.append({**l, **{nomes[c]: None for c in extras}})
            for a in achados:
                saida.append({**l, **{nomes[c]: a[c] for c in extras}})
        return Tabela(saida, self.colunas + [nomes[c] for c in extras])

    def pivot(self, indice: str, colunas: str, valores: str, agg: str | Callable = "soma") -> "Tabela":
        f = _agregador(agg)
        celulas: dict[Any, dict[str, list[Any]]] = {}
        novas: list[str] = []
        for l in self._linhas:
            nome = str(l[colunas])
            if nome not in novas:
                novas.append(nome)
            lista = celulas.setdefault(l[indice], {}).setdefault(nome, [])
            if l[valores] is not None:
                lista.append(l[valores])
        saida = []
        for chave, cols in celulas.items():
            r: Linha = {indice: chave}
            for n in novas:
                r[n] = f(cols[n]) if n in cols else None
            saida.append(r)
        return Tabela(saida, [indice] + novas)
