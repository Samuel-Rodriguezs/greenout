"""Hash de senha com sal (PBKDF2-HMAC-SHA256) e verificação em tempo constante.

AVISO: didático. Em produção prefira scrypt/argon2 e bibliotecas auditadas.
Formato armazenado: pbkdf2_sha256$iteracoes$sal_hex$hash_hex
"""
from __future__ import annotations

import hashlib
import hmac
import secrets

ITERACOES_PADRAO = 200_000
_ALG = "pbkdf2_sha256"


def hash_senha(senha: str, iteracoes: int = ITERACOES_PADRAO, sal: bytes | None = None) -> str:
    if iteracoes < 1:
        raise ValueError("iteracoes deve ser >= 1")
    sal = sal if sal is not None else secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, iteracoes)
    return f"{_ALG}${iteracoes}${sal.hex()}${h.hex()}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    """Retorna False para qualquer formato inválido (nunca lança)."""
    try:
        alg, it, sal_hex, h_hex = armazenado.split("$")
        if alg != _ALG:
            return False
        esperado = bytes.fromhex(h_hex)
        h = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal_hex), int(it))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(h, esperado)


def precisa_rehash(armazenado: str, iteracoes: int = ITERACOES_PADRAO) -> bool:
    try:
        return int(armazenado.split("$")[1]) < iteracoes
    except (IndexError, ValueError):
        return True
