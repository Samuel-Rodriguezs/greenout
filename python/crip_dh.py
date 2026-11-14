"""Diffie-Hellman didático com o grupo MODP 14 (RFC 3526, 2048 bits).

AVISO: apenas para estudo, sem autenticação nem derivação segura (use KDF real).
"""
from __future__ import annotations

import hashlib
import secrets

# RFC 3526, grupo 14.
P_MODP14 = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22"
    "514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6"
    "F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB"
    "9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E8603"
    "9B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF",
    16,
)
G_MODP14 = 2


def gerar_privada(p: int = P_MODP14) -> int:
    return 2 + secrets.randbelow(p - 3)


def publica(privada: int, p: int = P_MODP14, g: int = G_MODP14) -> int:
    return pow(g, privada, p)


def segredo_compartilhado(privada: int, publica_outro: int, p: int = P_MODP14) -> int:
    if not 2 <= publica_outro <= p - 2:
        raise ValueError("chave pública inválida")
    return pow(publica_outro, privada, p)


def derivar_chave(segredo: int) -> bytes:
    """Deriva 32 bytes via SHA-256 do segredo (simplificado)."""
    return hashlib.sha256(segredo.to_bytes((segredo.bit_length() + 7) // 8 or 1, "big")).digest()
