"""Segmento TCP: flags, opções (MSS) e serialização com checksum (RFC 793)."""
from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntFlag

from rede_checksum import checksum, verificar

PROTO_TCP = 6


class Flags(IntFlag):
    FIN = 0x01
    SYN = 0x02
    RST = 0x04
    PSH = 0x08
    ACK = 0x10
    URG = 0x20
    ECE = 0x40
    CWR = 0x80


@dataclass(frozen=True)
class SegmentoTCP:
    porta_origem: int
    porta_destino: int
    seq: int = 0
    ack: int = 0
    flags: Flags = Flags(0)
    janela: int = 65535
    carga: bytes = b""
    mss: int | None = None  # opção MSS (só faz sentido com SYN)
    urgente: int = 0


def descrever_flags(f: Flags) -> str:
    nomes = [fl.name for fl in Flags if f & fl]
    return "|".join(nomes) if nomes else "-"


def _opcoes(mss: int | None) -> bytes:
    return struct.pack("!BBH", 2, 4, mss) if mss is not None else b""


def _pseudo(origem: int, destino: int, comprimento: int) -> bytes:
    return struct.pack("!IIBBH", origem, destino, 0, PROTO_TCP, comprimento)


def serializar(s: SegmentoTCP, ip_origem: int, ip_destino: int) -> bytes:
    opcoes = _opcoes(s.mss)
    offset = (20 + len(opcoes)) // 4
    sem = struct.pack("!HHIIBBHHH", s.porta_origem, s.porta_destino,
                      s.seq & 0xFFFFFFFF, s.ack & 0xFFFFFFFF, offset << 4,
                      int(s.flags), s.janela, 0, s.urgente) + opcoes + s.carga
    soma = checksum(_pseudo(ip_origem, ip_destino, len(sem)) + sem)
    return sem[:16] + struct.pack("!H", soma) + sem[18:]


def parse(dados: bytes, ip_origem: int, ip_destino: int) -> SegmentoTCP:
    if len(dados) < 20:
        raise ValueError("segmento truncado")
    po, pd, seq, ack, off, fl, jan, _, urg = struct.unpack("!HHIIBBHHH", dados[:20])
    tam_cab = (off >> 4) * 4
    if tam_cab < 20 or tam_cab > len(dados):
        raise ValueError("data offset inválido")
    if not verificar(_pseudo(ip_origem, ip_destino, len(dados)) + dados):
        raise ValueError("checksum TCP inválido")
    mss = None
    ops = dados[20:tam_cab]
    i = 0
    while i < len(ops):
        tipo = ops[i]
        if tipo == 0:  # fim da lista
            break
        if tipo == 1:  # NOP
            i += 1
            continue
        if i + 1 >= len(ops) or ops[i + 1] < 2 or i + ops[i + 1] > len(ops):
            raise ValueError("opção TCP malformada")
        if tipo == 2 and ops[i + 1] == 4:
            mss = struct.unpack("!H", ops[i + 2:i + 4])[0]
        i += ops[i + 1]
    return SegmentoTCP(po, pd, seq, ack, Flags(fl), jan, dados[tam_cab:], mss, urg)


def consumo_de_seq(s: SegmentoTCP) -> int:
    """Quantidade de números de sequência consumidos (SYN e FIN contam 1)."""
    return len(s.carga) + bool(s.flags & Flags.SYN) + bool(s.flags & Flags.FIN)
