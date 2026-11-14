"""Runner de migrações versionadas para sqlite3, com checksum e rollback."""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass


class ErroMigracao(Exception):
    pass


@dataclass(frozen=True)
class Migracao:
    versao: int
    nome: str
    subir: str
    descer: str = ""

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.subir.encode("utf-8")).hexdigest()[:16]


def _comandos(sql: str) -> list[str]:
    """Divide um script em comandos completos (respeita ; dentro de strings/triggers)."""
    comandos, atual = [], ""
    for linha in sql.splitlines(keepends=True):
        atual += linha
        if sqlite3.complete_statement(atual):
            comandos.append(atual.strip())
            atual = ""
    if atual.strip():
        comandos.append(atual.strip())
    return comandos


class Migrador:
    def __init__(self, conexao: sqlite3.Connection, migracoes: list[Migracao]) -> None:
        versoes = [m.versao for m in migracoes]
        if len(set(versoes)) != len(versoes):
            raise ErroMigracao("versões duplicadas")
        if any(v <= 0 for v in versoes):
            raise ErroMigracao("versões devem ser positivas")
        self.con = conexao
        self.migracoes = sorted(migracoes, key=lambda m: m.versao)
        self.con.execute(
            "CREATE TABLE IF NOT EXISTS schema_migracoes ("
            "versao INTEGER PRIMARY KEY, nome TEXT NOT NULL, checksum TEXT NOT NULL)")
        self.con.commit()

    def aplicadas(self) -> list[int]:
        return [r[0] for r in self.con.execute("SELECT versao FROM schema_migracoes ORDER BY versao")]

    def versao_atual(self) -> int:
        return max(self.aplicadas(), default=0)

    def pendentes(self) -> list[Migracao]:
        feitas = set(self.aplicadas())
        return [m for m in self.migracoes if m.versao not in feitas]

    def _verificar_checksums(self) -> None:
        por_versao = {m.versao: m for m in self.migracoes}
        for versao, chk in self.con.execute("SELECT versao, checksum FROM schema_migracoes"):
            m = por_versao.get(versao)
            if m is None:
                raise ErroMigracao(f"migração aplicada {versao} não existe mais")
            if m.checksum != chk:
                raise ErroMigracao(f"migração {versao} foi alterada após aplicada")

    def _executar(self, sql: str, final: str, params: tuple) -> None:
        self.con.commit()
        self.con.execute("BEGIN")
        try:
            for cmd in _comandos(sql):
                self.con.execute(cmd)
            self.con.execute(final, params)
            self.con.commit()
        except sqlite3.Error as e:
            self.con.rollback()
            raise ErroMigracao(str(e)) from e

    def migrar(self, alvo: int | None = None) -> list[int]:
        self._verificar_checksums()
        aplicadas: list[int] = []
        for m in self.pendentes():
            if alvo is not None and m.versao > alvo:
                break
            try:
                self._executar(m.subir, "INSERT INTO schema_migracoes VALUES (?, ?, ?)",
                               (m.versao, m.nome, m.checksum))
            except ErroMigracao as e:
                raise ErroMigracao(f"falha na migração {m.versao} ({m.nome}): {e}") from e
            aplicadas.append(m.versao)
        return aplicadas

    def reverter(self, passos: int = 1) -> list[int]:
        self._verificar_checksums()
        por_versao = {m.versao: m for m in self.migracoes}
        revertidas: list[int] = []
        for versao in reversed(self.aplicadas()[-passos:] if passos > 0 else []):
            m = por_versao[versao]
            if not m.descer:
                raise ErroMigracao(f"migração {versao} não é reversível")
            self._executar(m.descer, "DELETE FROM schema_migracoes WHERE versao = ?", (versao,))
            revertidas.append(versao)
        return revertidas
