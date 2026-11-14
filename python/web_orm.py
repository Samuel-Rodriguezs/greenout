"""Mini-ORM sobre sqlite3 com CRUD básico."""
from __future__ import annotations

import re
import sqlite3
from typing import Any, ClassVar

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TIPOS = {"int": "INTEGER", "str": "TEXT", "float": "REAL", "bool": "INTEGER", "bytes": "BLOB"}


class RegistroNaoEncontrado(LookupError):
    pass


class Modelo:
    """Subclasse define `tabela` e `colunas` ({nome: 'int'|'str'|'float'|'bool'|'bytes'}).

    A coluna `id` INTEGER PRIMARY KEY AUTOINCREMENT é implícita.
    """

    tabela: ClassVar[str] = ""
    colunas: ClassVar[dict[str, str]] = {}
    conexao: ClassVar[sqlite3.Connection | None] = None

    def __init__(self, **valores: Any) -> None:
        desconhecidas = set(valores) - set(self.colunas) - {"id"}
        if desconhecidas:
            raise TypeError(f"colunas desconhecidas: {sorted(desconhecidas)}")
        self.id: int | None = valores.pop("id", None)
        for c in self.colunas:
            setattr(self, c, valores.get(c))

    @classmethod
    def _con(cls) -> sqlite3.Connection:
        if cls.conexao is None:
            raise RuntimeError("modelo sem conexão: use Modelo.vincular(conexao)")
        return cls.conexao

    @classmethod
    def vincular(cls, conexao: sqlite3.Connection) -> None:
        cls.conexao = conexao

    @classmethod
    def _validar(cls) -> None:
        if not _IDENT.match(cls.tabela):
            raise ValueError(f"tabela inválida: {cls.tabela!r}")
        for nome, tipo in cls.colunas.items():
            if not _IDENT.match(nome) or nome == "id":
                raise ValueError(f"coluna inválida: {nome!r}")
            if tipo not in _TIPOS:
                raise ValueError(f"tipo inválido: {tipo!r}")

    @classmethod
    def criar_tabela(cls) -> None:
        cls._validar()
        defs = ", ".join(f"{n} {_TIPOS[t]}" for n, t in cls.colunas.items())
        sql = f"CREATE TABLE IF NOT EXISTS {cls.tabela} (id INTEGER PRIMARY KEY AUTOINCREMENT"
        cls._con().execute(sql + (", " + defs if defs else "") + ")")

    @classmethod
    def _de_linha(cls, linha: sqlite3.Row | tuple) -> "Modelo":
        valores = dict(zip(["id", *cls.colunas], linha))
        for n, t in cls.colunas.items():
            if t == "bool" and valores[n] is not None:
                valores[n] = bool(valores[n])
        return cls(**valores)

    def _valores(self) -> list[Any]:
        return [getattr(self, c) for c in self.colunas]

    def salvar(self) -> "Modelo":
        con, cols = self._con(), list(self.colunas)
        if self.id is None:
            marcas = ", ".join("?" * len(cols))
            cur = con.execute(
                f"INSERT INTO {self.tabela} ({', '.join(cols)}) VALUES ({marcas})", self._valores())
            self.id = cur.lastrowid
        else:
            sets = ", ".join(f"{c} = ?" for c in cols)
            cur = con.execute(f"UPDATE {self.tabela} SET {sets} WHERE id = ?", [*self._valores(), self.id])
            if cur.rowcount == 0:
                raise RegistroNaoEncontrado(f"{self.tabela}#{self.id}")
        return self

    @classmethod
    def criar(cls, **valores: Any) -> "Modelo":
        return cls(**valores).salvar()

    @classmethod
    def buscar(cls, id: int) -> "Modelo":
        linha = cls._con().execute(
            f"SELECT id, {', '.join(cls.colunas)} FROM {cls.tabela} WHERE id = ?", [id]).fetchone()
        if linha is None:
            raise RegistroNaoEncontrado(f"{cls.tabela}#{id}")
        return cls._de_linha(linha)

    @classmethod
    def listar(cls, ordem: str = "id", limite: int | None = None, **filtros: Any) -> list["Modelo"]:
        permitidas = {"id", *cls.colunas}
        for f in filtros:
            if f not in permitidas:
                raise ValueError(f"filtro inválido: {f}")
        coluna_ordem = ordem.lstrip("-")
        if coluna_ordem not in permitidas:
            raise ValueError(f"ordem inválida: {ordem}")
        sql = f"SELECT id, {', '.join(cls.colunas)} FROM {cls.tabela}"
        if filtros:
            sql += " WHERE " + " AND ".join(
                f"{k} IS NULL" if v is None else f"{k} = ?" for k, v in filtros.items())
        sql += f" ORDER BY {coluna_ordem} {'DESC' if ordem.startswith('-') else 'ASC'}"
        params = [v for v in filtros.values() if v is not None]
        if limite is not None:
            sql += " LIMIT ?"
            params.append(int(limite))
        return [cls._de_linha(r) for r in cls._con().execute(sql, params)]

    @classmethod
    def contar(cls) -> int:
        return cls._con().execute(f"SELECT COUNT(*) FROM {cls.tabela}").fetchone()[0]

    def deletar(self) -> None:
        if self.id is None:
            raise ValueError("registro não salvo")
        self._con().execute(f"DELETE FROM {self.tabela} WHERE id = ?", [self.id])
        self.id = None

    def para_dict(self) -> dict[str, Any]:
        return {"id": self.id, **{c: getattr(self, c) for c in self.colunas}}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.para_dict()})"
