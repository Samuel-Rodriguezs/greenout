"""Esquema de compromisso (commitment) por hash: escondendo (nonce aleatório) e vinculante.

AVISO: didático. commit = SHA-256(len(nonce) || nonce || mensagem).
Também inclui o jogo "cara ou coroa por telefone" como aplicação.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import NamedTuple


class Compromisso(NamedTuple):
    valor: str  # hex público
    nonce: bytes  # segredo guardado até a revelação


def _h(nonce: bytes, msg: bytes) -> str:
    return hashlib.sha256(len(nonce).to_bytes(2, "big") + nonce + msg).hexdigest()


def comprometer(msg: bytes, nonce: bytes | None = None) -> Compromisso:
    nonce = nonce if nonce is not None else secrets.token_bytes(32)
    if not 1 <= len(nonce) <= 65535:
        raise ValueError("nonce deve ter entre 1 e 65535 bytes")
    return Compromisso(_h(nonce, msg), nonce)


def revelar_valido(valor: str, msg: bytes, nonce: bytes) -> bool:
    if not 1 <= len(nonce) <= 65535:
        return False
    return hmac.compare_digest(_h(nonce, msg), valor.lower())


def cara_ou_coroa(escolha_alice: str, bit_bob: int) -> str:
    """Alice se compromete com 'cara'/'coroa'; Bob manda um bit; resultado = XOR (0 -> cara)."""
    if escolha_alice not in ("cara", "coroa") or bit_bob not in (0, 1):
        raise ValueError("entrada inválida")
    bit_alice = 0 if escolha_alice == "cara" else 1
    return "cara" if bit_alice ^ bit_bob == 0 else "coroa"
