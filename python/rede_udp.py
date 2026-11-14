"""Datagrama UDP: cabeçalho de 8 bytes e pseudo-cabeçalho IPv4 (RFC 768)."""
from __future__ import annotations

import struct
from dataclasses import dataclass

from rede_checksum import checksum, verificar

PROTO_UDP = 17


def pseudo_cabecalho(origem: int, destino: int, protocolo: int, comprimento: int) -> bytes:
    return struct.pack("!IIBBH", origem, destino, 0, protocolo, comprimento)


@dataclass(frozen=True)
class DatagramaUDP:
    porta_origem: int
    porta_destino: int
    carga: bytes = b""
    checksum: int = 0

    @property
    def comprimento(self) -> int:
        return 8 + len(self.carga)


def serializar(d: DatagramaUDP, ip_origem: int, ip_destino: int) -> bytes:
    """Gera o datagrama com checksum calculado sobre o pseudo-cabeçalho."""
    if d.comprimento > 0xFFFF:
        raise ValueError("datagrama grande demais")
    sem = struct.pack("!HHHH", d.porta_origem, d.porta_destino, d.comprimento, 0) + d.carga
    soma = checksum(pseudo_cabecalho(ip_origem, ip_destino, PROTO_UDP, len(sem)) + sem)
    if soma == 0:
        soma = 0xFFFF  # 0 significa "sem checksum" em UDP/IPv4
    return sem[:6] + struct.pack("!H", soma) + sem[8:]


def parse(dados: bytes, ip_origem: int, ip_destino: int) -> DatagramaUDP:
    if len(dados) < 8:
        raise ValueError("datagrama truncado")
    po, pd, comp, soma = struct.unpack("!HHHH", dados[:8])
    if comp != len(dados) or comp < 8:
        raise ValueError("campo de comprimento inconsistente")
    if soma != 0 and not verificar(pseudo_cabecalho(ip_origem, ip_destino, PROTO_UDP, comp) + dados):
        raise ValueError("checksum UDP inválido")
    return DatagramaUDP(po, pd, dados[8:], soma)
