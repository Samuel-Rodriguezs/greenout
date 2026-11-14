"""Autenticação HTTP Basic e Bearer como middlewares."""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import os
from typing import Any, Callable

from web_http import Requisicao, Resposta
from web_middleware import Manipulador, Middleware


def parse_basic(cabecalho: str | None) -> tuple[str, str] | None:
    """'Basic base64(user:senha)' -> (user, senha); None se ausente/malformado."""
    if not cabecalho:
        return None
    esquema, _, cred = cabecalho.strip().partition(" ")
    if esquema.lower() != "basic" or not cred.strip():
        return None
    try:
        texto = base64.b64decode(cred.strip(), validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return None
    usuario, sep, senha = texto.partition(":")
    return (usuario, senha) if sep and usuario else None


def parse_bearer(cabecalho: str | None) -> str | None:
    if not cabecalho:
        return None
    esquema, _, token = cabecalho.strip().partition(" ")
    token = token.strip()
    if esquema.lower() != "bearer" or not token or " " in token:
        return None
    return token


def codificar_basic(usuario: str, senha: str) -> str:
    return "Basic " + base64.b64encode(f"{usuario}:{senha}".encode()).decode()


def hash_senha(senha: str, sal: bytes | None = None, iteracoes: int = 120_000) -> str:
    sal = sal if sal is not None else os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, iteracoes)
    return f"pbkdf2${iteracoes}${sal.hex()}${h.hex()}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        _, it, sal, h = armazenado.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal), int(it))
        return hmac.compare_digest(calc, bytes.fromhex(h))
    except (ValueError, TypeError):
        return False


def _nao_autorizado(esquema: str, realm: str, detalhe: str | None = None) -> Resposta:
    resp = Resposta.de_texto("Não autorizado", 401)
    desafio = f'{esquema} realm="{realm}"'
    if detalhe:
        desafio += f', error="{detalhe}"'
    resp.cabecalhos["WWW-Authenticate"] = desafio
    return resp


def mw_basic(usuarios: dict[str, str], realm: str = "restrito") -> Middleware:
    """usuarios: {nome: hash_senha(...)}. Compara sem vazar existência do usuário pelo tempo."""
    falso = hash_senha("x", b"0" * 16)

    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        cred = parse_basic(req.cabecalhos.get("Authorization"))
        if cred is None:
            return _nao_autorizado("Basic", realm)
        usuario, senha = cred
        ok = verificar_senha(senha, usuarios.get(usuario, falso)) and usuario in usuarios
        if not ok:
            return _nao_autorizado("Basic", realm)
        req.contexto["usuario"] = usuario
        return proximo(req)
    return mw


def mw_bearer(verificador: Callable[[str], Any | None], realm: str = "api") -> Middleware:
    """verificador(token) devolve a identidade (truthy) ou None se inválido."""
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        cab = req.cabecalhos.get("Authorization")
        token = parse_bearer(cab)
        if token is None:
            return _nao_autorizado("Bearer", realm, "invalid_request" if cab else None)
        identidade = verificador(token)
        if not identidade:
            return _nao_autorizado("Bearer", realm, "invalid_token")
        req.contexto["identidade"] = identidade
        return proximo(req)
    return mw


def exigir_escopo(escopo: str) -> Middleware:
    """Depois de mw_bearer: identidade deve ser dict com lista 'escopos'."""
    def mw(req: Requisicao, proximo: Manipulador) -> Resposta:
        ident = req.contexto.get("identidade")
        if not isinstance(ident, dict) or escopo not in ident.get("escopos", ()):
            return Resposta.de_texto("Proibido", 403)
        return proximo(req)
    return mw
