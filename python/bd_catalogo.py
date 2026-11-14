"""Catálogo de esquemas: tabelas, colunas, chaves primárias, índices e estatísticas.

Nomes são insensíveis a maiúsculas (guardados em minúsculas). O catálogo é
persistido como JSON com número de versão e gravação atômica.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional

from bd_sql_parser import CriarTabela

VERSAO = 1
NORMALIZA = {"INT": "INT", "INTEGER": "INT", "REAL": "REAL", "FLOAT": "REAL", "TEXT": "TEXT",
             "VARCHAR": "TEXT", "BOOL": "BOOL", "BOOLEAN": "BOOL"}


class ErroCatalogo(Exception):
    pass


@dataclass
class Coluna:
    nome: str
    tipo: str
    chave_primaria: bool = False


@dataclass
class Indice:
    nome: str
    tabela: str
    coluna: str
    unico: bool = False


@dataclass
class Tabela:
    nome: str
    colunas: list[Coluna]
    n_linhas: int = 0
    indices: dict[str, Indice] = field(default_factory=dict)

    def posicao(self, coluna: str) -> int:
        c = coluna.lower()
        for i, col in enumerate(self.colunas):
            if col.nome == c:
                return i
        raise ErroCatalogo(f"coluna inexistente: {self.nome}.{coluna}")

    def esquema(self) -> list[tuple[str, str]]:
        return [(c.nome, c.tipo) for c in self.colunas]

    @property
    def chave_primaria(self) -> Optional[str]:
        return next((c.nome for c in self.colunas if c.chave_primaria), None)

    def indice_da_coluna(self, coluna: str) -> Optional[Indice]:
        c = coluna.lower()
        return next((i for i in self.indices.values() if i.coluna == c), None)


class Catalogo:
    def __init__(self) -> None:
        self.tabelas: dict[str, Tabela] = {}

    def criar_tabela(self, nome: str, colunas: list[tuple[str, str, bool]]) -> Tabela:
        n = nome.lower()
        if n in self.tabelas:
            raise ErroCatalogo(f"tabela já existe: {nome}")
        if not colunas:
            raise ErroCatalogo("tabela precisa de ao menos uma coluna")
        cols: list[Coluna] = []
        for cn, tipo, pk in colunas:
            if tipo.upper() not in NORMALIZA:
                raise ErroCatalogo(f"tipo desconhecido: {tipo}")
            if cn.lower() in {c.nome for c in cols}:
                raise ErroCatalogo(f"coluna duplicada: {cn}")
            cols.append(Coluna(cn.lower(), NORMALIZA[tipo.upper()], pk))
        if sum(c.chave_primaria for c in cols) > 1:
            raise ErroCatalogo("mais de uma chave primária")
        t = Tabela(n, cols)
        self.tabelas[n] = t
        pk = t.chave_primaria
        if pk:
            t.indices[f"pk_{n}"] = Indice(f"pk_{n}", n, pk, True)
        return t

    def criar_de_ast(self, cmd: CriarTabela) -> Tabela:
        return self.criar_tabela(cmd.nome, cmd.colunas)

    def tabela(self, nome: str) -> Tabela:
        try:
            return self.tabelas[nome.lower()]
        except KeyError:
            raise ErroCatalogo(f"tabela inexistente: {nome}") from None

    def remover_tabela(self, nome: str) -> None:
        self.tabela(nome)
        del self.tabelas[nome.lower()]

    def criar_indice(self, nome: str, tabela: str, coluna: str, unico: bool = False) -> Indice:
        t = self.tabela(tabela)
        t.posicao(coluna)
        n = nome.lower()
        if any(n in x.indices for x in self.tabelas.values()):
            raise ErroCatalogo(f"índice já existe: {nome}")
        if t.indice_da_coluna(coluna):
            raise ErroCatalogo(f"coluna já indexada: {coluna}")
        i = Indice(n, t.nome, coluna.lower(), unico)
        t.indices[n] = i
        return i

    def remover_indice(self, nome: str) -> None:
        n = nome.lower()
        for t in self.tabelas.values():
            if n in t.indices:
                if n == f"pk_{t.nome}":
                    raise ErroCatalogo("índice da chave primária não pode ser removido")
                del t.indices[n]
                return
        raise ErroCatalogo(f"índice inexistente: {nome}")

    def resolver_coluna(self, coluna: str, tabelas: list[str]) -> tuple[str, int]:
        """Acha a tabela dona de uma coluna não qualificada; erra se ausente ou ambígua."""
        achadas = []
        for nome in tabelas:
            t = self.tabela(nome)
            if any(c.nome == coluna.lower() for c in t.colunas):
                achadas.append((t.nome, t.posicao(coluna)))
        if not achadas:
            raise ErroCatalogo(f"coluna inexistente: {coluna}")
        if len(achadas) > 1:
            raise ErroCatalogo(f"coluna ambígua: {coluna}")
        return achadas[0]

    # ---- persistência ----
    def para_dict(self) -> dict:
        return {"versao": VERSAO, "tabelas": [
            {"nome": t.nome, "n_linhas": t.n_linhas,
             "colunas": [[c.nome, c.tipo, c.chave_primaria] for c in t.colunas],
             "indices": [[i.nome, i.coluna, i.unico] for i in t.indices.values()]}
            for t in self.tabelas.values()]}

    @classmethod
    def de_dict(cls, d: dict) -> "Catalogo":
        if d.get("versao") != VERSAO:
            raise ErroCatalogo(f"versão de catálogo não suportada: {d.get('versao')}")
        cat = cls()
        try:
            for td in d["tabelas"]:
                t = Tabela(td["nome"], [Coluna(n, ti, pk) for n, ti, pk in td["colunas"]], td["n_linhas"])
                for nome, col, unico in td["indices"]:
                    t.indices[nome] = Indice(nome, t.nome, col, unico)
                cat.tabelas[t.nome] = t
        except (KeyError, TypeError, ValueError) as e:
            raise ErroCatalogo(f"catálogo corrompido: {e}") from e
        return cat

    def salvar(self, caminho: str) -> None:
        tmp = caminho + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.para_dict(), f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, caminho)

    @classmethod
    def carregar(cls, caminho: str) -> "Catalogo":
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return cls.de_dict(json.load(f))
        except json.JSONDecodeError as e:
            raise ErroCatalogo(f"catálogo corrompido: {e}") from e
