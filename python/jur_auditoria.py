"""Log de auditoria imutável: cada registro encadeia o hash SHA-256 do anterior."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

GENESIS = "0" * 64


@dataclass(frozen=True)
class Registro:
    indice: int
    quando: datetime
    usuario: str
    acao: str
    detalhes: dict[str, str]
    hash_anterior: str
    hash: str


def _calcular(indice: int, quando: datetime, usuario: str, acao: str, detalhes: dict[str, str], anterior: str) -> str:
    corpo = json.dumps([indice, quando.isoformat(), usuario, acao, detalhes, anterior],
                       sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(corpo.encode("utf-8")).hexdigest()


class LogAuditoria:
    def __init__(self) -> None:
        self._registros: list[Registro] = []

    def registrar(self, quando: datetime, usuario: str, acao: str, detalhes: dict[str, str] | None = None) -> Registro:
        if not usuario.strip() or not acao.strip():
            raise ValueError("usuário e ação são obrigatórios")
        if self._registros and quando < self._registros[-1].quando:
            raise ValueError("registro anterior ao último do log")
        det = dict(detalhes or {})
        anterior = self._registros[-1].hash if self._registros else GENESIS
        i = len(self._registros)
        r = Registro(i, quando, usuario, acao, det, anterior, _calcular(i, quando, usuario, acao, det, anterior))
        self._registros.append(r)
        return r

    @property
    def registros(self) -> tuple[Registro, ...]:
        """Visão imutável: não há API para alterar ou remover entradas."""
        return tuple(self._registros)

    def verificar(self) -> int | None:
        """Índice do primeiro registro adulterado, ou None se a cadeia está íntegra."""
        return verificar_cadeia(self._registros)

    def do_usuario(self, usuario: str) -> list[Registro]:
        return [r for r in self._registros if r.usuario == usuario]

    def __len__(self) -> int:
        return len(self._registros)


def verificar_cadeia(registros: list[Registro] | tuple[Registro, ...]) -> int | None:
    anterior = GENESIS
    for i, r in enumerate(registros):
        if r.indice != i or r.hash_anterior != anterior:
            return i
        if r.hash != _calcular(r.indice, r.quando, r.usuario, r.acao, r.detalhes, r.hash_anterior):
            return i
        anterior = r.hash
    return None
