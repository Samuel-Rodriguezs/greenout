"""Repository: persistência de clientes abstraída (memória e SQLite)."""
from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Cliente:
    id: Optional[int]
    nome: str
    email: str


class RepositorioClientes(ABC):
    @abstractmethod
    def salvar(self, c: Cliente) -> Cliente: ...

    @abstractmethod
    def obter(self, id_: int) -> Optional[Cliente]: ...

    @abstractmethod
    def listar(self) -> list[Cliente]: ...

    @abstractmethod
    def remover(self, id_: int) -> bool: ...

    def buscar_por_email(self, email: str) -> Optional[Cliente]:
        return next((c for c in self.listar() if c.email == email), None)


class RepositorioMemoria(RepositorioClientes):
    def __init__(self) -> None:
        self._dados: dict[int, Cliente] = {}
        self._seq = 0

    def salvar(self, c: Cliente) -> Cliente:
        if c.id is None:
            self._seq += 1
            c = Cliente(self._seq, c.nome, c.email)
        self._dados[c.id] = Cliente(c.id, c.nome, c.email)
        return c

    def obter(self, id_: int) -> Optional[Cliente]:
        return self._dados.get(id_)

    def listar(self) -> list[Cliente]:
        return [self._dados[k] for k in sorted(self._dados)]

    def remover(self, id_: int) -> bool:
        return self._dados.pop(id_, None) is not None


class RepositorioSqlite(RepositorioClientes):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        conn.execute("CREATE TABLE IF NOT EXISTS clientes "
                     "(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT)")

    def salvar(self, c: Cliente) -> Cliente:
        if c.id is None:
            cur = self._conn.execute(
                "INSERT INTO clientes (nome, email) VALUES (?, ?)", (c.nome, c.email))
            return Cliente(cur.lastrowid, c.nome, c.email)
        self._conn.execute("INSERT OR REPLACE INTO clientes VALUES (?, ?, ?)",
                           (c.id, c.nome, c.email))
        return c

    def obter(self, id_: int) -> Optional[Cliente]:
        row = self._conn.execute(
            "SELECT id, nome, email FROM clientes WHERE id = ?", (id_,)).fetchone()
        return Cliente(*row) if row else None

    def listar(self) -> list[Cliente]:
        rows = self._conn.execute(
            "SELECT id, nome, email FROM clientes ORDER BY id").fetchall()
        return [Cliente(*r) for r in rows]

    def remover(self, id_: int) -> bool:
        return self._conn.execute(
            "DELETE FROM clientes WHERE id = ?", (id_,)).rowcount > 0
