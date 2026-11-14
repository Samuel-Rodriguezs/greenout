"""Builder: construção fluente de consultas SQL SELECT."""
from __future__ import annotations


class Consulta:
    def __init__(self, sql: str, params: tuple) -> None:
        self.sql = sql
        self.params = params


class ConsultaBuilder:
    def __init__(self, tabela: str) -> None:
        self._tabela = tabela
        self._colunas: list[str] = []
        self._filtros: list[str] = []
        self._params: list = []
        self._ordem: str | None = None
        self._limite: int | None = None

    def colunas(self, *cols: str) -> "ConsultaBuilder":
        self._colunas.extend(cols)
        return self

    def onde(self, condicao: str, *params) -> "ConsultaBuilder":
        self._filtros.append(condicao)
        self._params.extend(params)
        return self

    def ordenar(self, coluna: str, desc: bool = False) -> "ConsultaBuilder":
        self._ordem = f"{coluna} {'DESC' if desc else 'ASC'}"
        return self

    def limitar(self, n: int) -> "ConsultaBuilder":
        if n < 0:
            raise ValueError("limite negativo")
        self._limite = n
        return self

    def construir(self) -> Consulta:
        cols = ", ".join(self._colunas) or "*"
        sql = f"SELECT {cols} FROM {self._tabela}"
        if self._filtros:
            sql += " WHERE " + " AND ".join(self._filtros)
        if self._ordem:
            sql += f" ORDER BY {self._ordem}"
        if self._limite is not None:
            sql += f" LIMIT {self._limite}"
        return Consulta(sql, tuple(self._params))
