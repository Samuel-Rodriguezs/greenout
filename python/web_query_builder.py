"""Query builder SQL fluente e parametrizado (valores nunca são interpolados)."""
from __future__ import annotations

import re
from typing import Any

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")
_OPS = {"=", "!=", "<>", "<", "<=", ">", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN", "IS", "IS NOT"}


def _ident(nome: str) -> str:
    if nome != "*" and not _IDENT.match(nome):
        raise ValueError(f"identificador inválido: {nome!r}")
    return nome


class Consulta:
    """SELECT fluente. Cada método devolve self; construir() -> (sql, params)."""

    def __init__(self, tabela: str) -> None:
        self._tabela = _ident(tabela)
        self._colunas: list[str] = ["*"]
        self._condicoes: list[tuple[str, str, Any]] = []  # (conector, sql, valor)
        self._params_cond: list[list[Any]] = []
        self._ordem: list[str] = []
        self._limite: int | None = None
        self._deslocamento: int | None = None
        self._joins: list[str] = []
        self._agrupar: list[str] = []
        self._distinto = False

    def selecionar(self, *colunas: str) -> "Consulta":
        self._colunas = [_ident(c) for c in colunas] or ["*"]
        return self

    def distinto(self) -> "Consulta":
        self._distinto = True
        return self

    def juntar(self, tabela: str, esquerda: str, direita: str, tipo: str = "INNER") -> "Consulta":
        if tipo.upper() not in ("INNER", "LEFT"):
            raise ValueError("tipo de join inválido")
        self._joins.append(f"{tipo.upper()} JOIN {_ident(tabela)} ON {_ident(esquerda)} = {_ident(direita)}")
        return self

    def onde(self, coluna: str, op_ou_valor: Any, valor: Any = ...) -> "Consulta":
        return self._add("AND", coluna, op_ou_valor, valor)

    def ou_onde(self, coluna: str, op_ou_valor: Any, valor: Any = ...) -> "Consulta":
        return self._add("OR", coluna, op_ou_valor, valor)

    def _add(self, conector: str, coluna: str, op_ou_valor: Any, valor: Any) -> "Consulta":
        if valor is ...:
            op, valor = "=", op_ou_valor
        else:
            op = str(op_ou_valor).upper()
        if op not in _OPS:
            raise ValueError(f"operador inválido: {op}")
        col = _ident(coluna)
        if op in ("IN", "NOT IN"):
            itens = list(valor)
            if not itens:
                sql, params = ("1 = 0" if op == "IN" else "1 = 1"), []
            else:
                sql = f"{col} {op} ({', '.join('?' * len(itens))})"
                params = itens
        elif valor is None:
            if op not in ("=", "IS", "!=", "<>", "IS NOT"):
                raise ValueError("NULL só com =, !=, IS ou IS NOT")
            sql = f"{col} {'IS' if op in ('=', 'IS') else 'IS NOT'} NULL"
            params = []
        else:
            sql, params = f"{col} {op} ?", [valor]
        self._condicoes.append((conector, sql, None))
        self._params_cond.append(params)
        return self

    def ordenar(self, coluna: str, descendente: bool = False) -> "Consulta":
        self._ordem.append(f"{_ident(coluna)} {'DESC' if descendente else 'ASC'}")
        return self

    def agrupar_por(self, *colunas: str) -> "Consulta":
        self._agrupar = [_ident(c) for c in colunas]
        return self

    def limite(self, n: int, deslocamento: int | None = None) -> "Consulta":
        if n < 0 or (deslocamento is not None and deslocamento < 0):
            raise ValueError("limite/deslocamento negativo")
        self._limite, self._deslocamento = int(n), deslocamento
        return self

    def construir(self) -> tuple[str, list[Any]]:
        sql = f"SELECT {'DISTINCT ' if self._distinto else ''}{', '.join(self._colunas)} FROM {self._tabela}"
        if self._joins:
            sql += " " + " ".join(self._joins)
        params: list[Any] = []
        if self._condicoes:
            partes = []
            for i, ((conector, frag, _), ps) in enumerate(zip(self._condicoes, self._params_cond)):
                partes.append(frag if i == 0 else f"{conector} {frag}")
                params.extend(ps)
            sql += " WHERE " + " ".join(partes)
        if self._agrupar:
            sql += " GROUP BY " + ", ".join(self._agrupar)
        if self._ordem:
            sql += " ORDER BY " + ", ".join(self._ordem)
        if self._limite is not None:
            sql += f" LIMIT {self._limite}"
            if self._deslocamento is not None:
                sql += f" OFFSET {int(self._deslocamento)}"
        return sql, params


def inserir(tabela: str, valores: dict[str, Any]) -> tuple[str, list[Any]]:
    if not valores:
        raise ValueError("nenhum valor para inserir")
    cols = [_ident(c) for c in valores]
    return (f"INSERT INTO {_ident(tabela)} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
            list(valores.values()))


def atualizar(tabela: str, valores: dict[str, Any], onde: dict[str, Any]) -> tuple[str, list[Any]]:
    if not valores:
        raise ValueError("nenhum valor para atualizar")
    if not onde:
        raise ValueError("UPDATE sem condição não é permitido")
    sets = ", ".join(f"{_ident(c)} = ?" for c in valores)
    cond = " AND ".join(f"{_ident(c)} = ?" for c in onde)
    return f"UPDATE {_ident(tabela)} SET {sets} WHERE {cond}", list(valores.values()) + list(onde.values())


def remover(tabela: str, onde: dict[str, Any]) -> tuple[str, list[Any]]:
    if not onde:
        raise ValueError("DELETE sem condição não é permitido")
    cond = " AND ".join(f"{_ident(c)} = ?" for c in onde)
    return f"DELETE FROM {_ident(tabela)} WHERE {cond}", list(onde.values())
