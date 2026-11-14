"""JWT HS256: codificação e decodificação com validação de assinatura e `exp`/`nbf`.

AVISO: didático; não use em produção (prefira bibliotecas auditadas).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


class JWTInvalido(ValueError):
    pass


def _b64(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode()


def _unb64(texto: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))
    except Exception as e:  # noqa: BLE001
        raise JWTInvalido("base64url inválido") from e


def _json(obj: Any) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode()


def codificar(payload: dict[str, Any], segredo: bytes) -> str:
    cab = _b64(_json({"alg": "HS256", "typ": "JWT"}))
    corpo = _b64(_json(payload))
    assin = hmac.new(segredo, f"{cab}.{corpo}".encode(), hashlib.sha256).digest()
    return f"{cab}.{corpo}.{_b64(assin)}"


def decodificar(token: str, segredo: bytes, agora: float | None = None) -> dict[str, Any]:
    partes = token.split(".")
    if len(partes) != 3:
        raise JWTInvalido("token deve ter 3 partes")
    cab_s, corpo_s, assin_s = partes
    try:
        cab = json.loads(_unb64(cab_s))
        payload = json.loads(_unb64(corpo_s))
    except json.JSONDecodeError as e:
        raise JWTInvalido("JSON inválido") from e
    if not isinstance(cab, dict) or cab.get("alg") != "HS256":
        raise JWTInvalido("algoritmo não suportado")  # bloqueia alg=none
    esperado = hmac.new(segredo, f"{cab_s}.{corpo_s}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(esperado, _unb64(assin_s)):
        raise JWTInvalido("assinatura inválida")
    if not isinstance(payload, dict):
        raise JWTInvalido("payload deve ser objeto")
    agora = time.time() if agora is None else agora
    if "exp" in payload and agora >= payload["exp"]:
        raise JWTInvalido("token expirado")
    if "nbf" in payload and agora < payload["nbf"]:
        raise JWTInvalido("token ainda não válido")
    return payload
