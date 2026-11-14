"""Serializador JSON com tipos extras (datetime, date, time, Decimal, UUID, Enum, set, bytes, dataclass)."""
from __future__ import annotations

import base64
import dataclasses
import json
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any

_TAG = "__tipo__"


def _para_json(o: Any, marcado: bool) -> Any:
    def m(tipo: str, valor: Any) -> Any:
        return {_TAG: tipo, "valor": valor} if marcado else valor

    if isinstance(o, datetime):  # antes de date: datetime é subclasse
        return m("datetime", o.isoformat())
    if isinstance(o, date):
        return m("date", o.isoformat())
    if isinstance(o, time):
        return m("time", o.isoformat())
    if isinstance(o, Decimal):
        if not o.is_finite():
            raise ValueError("Decimal não finito não é serializável")
        return m("decimal", str(o))
    if isinstance(o, uuid.UUID):
        return m("uuid", str(o))
    if isinstance(o, Enum):
        return o.value
    if isinstance(o, (set, frozenset)):
        try:
            return m("set", sorted(o))
        except TypeError:
            return m("set", list(o))
    if isinstance(o, (bytes, bytearray)):
        return m("bytes", base64.b64encode(bytes(o)).decode("ascii"))
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        return {f.name: getattr(o, f.name) for f in dataclasses.fields(o)}
    raise TypeError(f"objeto do tipo {type(o).__name__} não é serializável em JSON")


def dumps(obj: Any, marcado: bool = False, **kw: Any) -> str:
    """marcado=True embrulha tipos especiais em {"__tipo__", "valor"} para permitir `loads` fiel."""
    return json.dumps(obj, default=lambda o: _para_json(o, marcado), ensure_ascii=False, **kw)


def _hook(d: dict[str, Any]) -> Any:
    tipo = d.get(_TAG)
    if tipo is None or set(d) != {_TAG, "valor"}:
        return d
    v = d["valor"]
    try:
        if tipo == "datetime":
            return datetime.fromisoformat(v)
        if tipo == "date":
            return date.fromisoformat(v)
        if tipo == "time":
            return time.fromisoformat(v)
        if tipo == "decimal":
            return Decimal(v)
        if tipo == "uuid":
            return uuid.UUID(v)
        if tipo == "set":
            return set(v)
        if tipo == "bytes":
            return base64.b64decode(v)
    except (ValueError, TypeError, ArithmeticError) as e:
        raise ValueError(f"valor inválido para {tipo}: {v!r}") from e
    raise ValueError(f"tipo desconhecido: {tipo}")


def loads(texto: str) -> Any:
    return json.loads(texto, object_hook=_hook)
