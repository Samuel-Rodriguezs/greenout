"""Quadros Ethernet II com FCS CRC-32 (IEEE 802.3) e tag VLAN 802.1Q opcional."""
from __future__ import annotations

import struct
from dataclasses import dataclass

TAM_MIN_CARGA = 46
TAM_MAX_CARGA = 1500
ETHERTYPE_VLAN = 0x8100


def _tabela_crc32() -> list[int]:
    tabela = []
    for n in range(256):
        c = n
        for _ in range(8):
            c = (c >> 1) ^ 0xEDB88320 if c & 1 else c >> 1
        tabela.append(c)
    return tabela


_TABELA = _tabela_crc32()


def crc32(dados: bytes) -> int:
    """CRC-32 refletido (poly 0x04C11DB7), init/xorout 0xFFFFFFFF."""
    c = 0xFFFFFFFF
    for b in dados:
        c = _TABELA[(c ^ b) & 0xFF] ^ (c >> 8)
    return c ^ 0xFFFFFFFF


@dataclass(frozen=True)
class Quadro:
    destino: int  # MAC de 48 bits
    origem: int
    ethertype: int
    carga: bytes
    vlan: int | None = None  # VID de 12 bits


def serializar(q: Quadro) -> bytes:
    """Cabeçalho + carga (com padding até 46 bytes) + FCS."""
    if len(q.carga) > TAM_MAX_CARGA:
        raise ValueError("carga excede a MTU de 1500 bytes")
    cab = q.destino.to_bytes(6, "big") + q.origem.to_bytes(6, "big")
    if q.vlan is not None:
        if not 0 <= q.vlan < 4096:
            raise ValueError("VID deve estar entre 0 e 4095")
        cab += struct.pack("!HH", ETHERTYPE_VLAN, q.vlan)
    cab += struct.pack("!H", q.ethertype)
    corpo = q.carga + bytes(max(0, TAM_MIN_CARGA - len(q.carga)))
    sem_fcs = cab + corpo
    return sem_fcs + struct.pack("<I", crc32(sem_fcs))  # FCS sai com o LSB primeiro


def parse(dados: bytes) -> Quadro:
    """Valida o FCS. O padding não pode ser removido sem um campo de tamanho,
    então `carga` volta com o padding quando a carga original tinha < 46 bytes."""
    if len(dados) < 64:
        raise ValueError("quadro menor que o mínimo de 64 bytes")
    sem_fcs, fcs = dados[:-4], struct.unpack("<I", dados[-4:])[0]
    if crc32(sem_fcs) != fcs:
        raise ValueError("FCS inválido")
    destino = int.from_bytes(sem_fcs[0:6], "big")
    origem = int.from_bytes(sem_fcs[6:12], "big")
    tipo = struct.unpack("!H", sem_fcs[12:14])[0]
    vlan = None
    pos = 14
    if tipo == ETHERTYPE_VLAN:
        tci, tipo = struct.unpack("!HH", sem_fcs[14:18])
        vlan = tci & 0x0FFF
        pos = 18
    return Quadro(destino, origem, tipo, sem_fcs[pos:], vlan)
