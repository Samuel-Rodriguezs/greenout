"""Cabeçalho IPv4: serialização e parse com struct, TTL e fragmentação."""
from __future__ import annotations

import struct
from dataclasses import dataclass, replace

from rede_checksum import checksum, verificar

FLAG_DF = 0b010
FLAG_MF = 0b001
PROTO_ICMP, PROTO_TCP, PROTO_UDP = 1, 6, 17


@dataclass(frozen=True)
class CabecalhoIPv4:
    origem: int
    destino: int
    protocolo: int
    comprimento_total: int = 20
    ttl: int = 64
    identificacao: int = 0
    flags: int = 0
    deslocamento: int = 0  # em unidades de 8 bytes
    tos: int = 0
    opcoes: bytes = b""

    @property
    def ihl(self) -> int:
        return 5 + len(self.opcoes) // 4

    @property
    def mais_fragmentos(self) -> bool:
        return bool(self.flags & FLAG_MF)

    @property
    def nao_fragmentar(self) -> bool:
        return bool(self.flags & FLAG_DF)


def serializar(c: CabecalhoIPv4) -> bytes:
    if len(c.opcoes) % 4 or len(c.opcoes) > 40:
        raise ValueError("opções devem ter múltiplo de 4 bytes (máx. 40)")
    if not 0 <= c.ttl <= 255 or not 0 <= c.deslocamento < 8192:
        raise ValueError("ttl ou deslocamento fora da faixa")
    campos = (
        (4 << 4) | c.ihl, c.tos, c.comprimento_total, c.identificacao,
        (c.flags << 13) | c.deslocamento, c.ttl, c.protocolo, 0,
        c.origem, c.destino,
    )
    sem = struct.pack("!BBHHHBBHII", *campos) + c.opcoes
    soma = checksum(sem)
    return sem[:10] + struct.pack("!H", soma) + sem[12:]


def parse(dados: bytes) -> CabecalhoIPv4:
    if len(dados) < 20:
        raise ValueError("cabeçalho truncado")
    vi, tos, total, ident, ff, ttl, proto, _, src, dst = struct.unpack("!BBHHHBBHII", dados[:20])
    if vi >> 4 != 4:
        raise ValueError("versão não é 4")
    ihl = vi & 0x0F
    if ihl < 5 or len(dados) < ihl * 4:
        raise ValueError("IHL inválido")
    if not verificar(dados[: ihl * 4]):
        raise ValueError("checksum do cabeçalho inválido")
    return CabecalhoIPv4(src, dst, proto, total, ttl, ident, ff >> 13, ff & 0x1FFF,
                         tos, dados[20: ihl * 4])


def decrementar_ttl(c: CabecalhoIPv4) -> CabecalhoIPv4:
    """Roteador: TTL-1; se chegar a 0 o pacote deve ser descartado."""
    if c.ttl <= 1:
        raise TimeoutError("TTL expirado")
    return replace(c, ttl=c.ttl - 1)


def fragmentar(c: CabecalhoIPv4, carga: bytes, mtu: int) -> list[tuple[CabecalhoIPv4, bytes]]:
    """Fragmenta a carga para a MTU dada, respeitando o bit DF."""
    tam_cab = c.ihl * 4
    if len(carga) + tam_cab <= mtu:
        return [(replace(c, comprimento_total=tam_cab + len(carga)), carga)]
    if c.nao_fragmentar:
        raise ValueError("pacote com DF excede a MTU")
    por_frag = ((mtu - tam_cab) // 8) * 8
    if por_frag <= 0:
        raise ValueError("MTU pequena demais")
    saida = []
    for ini in range(0, len(carga), por_frag):
        parte = carga[ini: ini + por_frag]
        ultimo = ini + por_frag >= len(carga)
        # o último fragmento herda o MF original (fragmentação de fragmento)
        mf = c.flags & FLAG_MF if ultimo else FLAG_MF
        flags = (c.flags & ~FLAG_MF) | mf
        saida.append((replace(c, comprimento_total=tam_cab + len(parte), flags=flags,
                              deslocamento=c.deslocamento + ini // 8), parte))
    return saida


def remontar(fragmentos: list[tuple[CabecalhoIPv4, bytes]]) -> bytes:
    """Reconstrói a carga; exige fragmentos contíguos e o último sem MF."""
    ordenados = sorted(fragmentos, key=lambda f: f[0].deslocamento)
    if not ordenados:
        raise ValueError("sem fragmentos")
    esperado = ordenados[0][0].deslocamento
    if esperado != 0:
        raise ValueError("falta o primeiro fragmento")
    buf = b""
    for cab, parte in ordenados:
        if cab.deslocamento * 8 != len(buf):
            raise ValueError("fragmentos não contíguos")
        buf += parte
    if ordenados[-1][0].mais_fragmentos:
        raise ValueError("falta o último fragmento")
    return buf
