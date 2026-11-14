"""CRC de blocos de dados (CRC-8, CRC-16/CCITT-FALSE, CRC-32) e verificação."""
from __future__ import annotations


def crc_generico(dados: bytes, largura: int, poli: int, init: int, refletir: bool, xor_final: int) -> int:
    """CRC parametrizável (modelo Rocksoft)."""
    topo = 1 << (largura - 1)
    mascara = (1 << largura) - 1
    if refletir:
        poli_r = int(f"{poli:0{largura}b}"[::-1], 2)
        crc = init
        for b in dados:
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ poli_r if crc & 1 else crc >> 1
        return (crc ^ xor_final) & mascara
    crc = init
    for b in dados:
        crc ^= b << (largura - 8)
        for _ in range(8):
            crc = ((crc << 1) ^ poli) if crc & topo else crc << 1
            crc &= mascara
    return (crc ^ xor_final) & mascara


def crc8(dados: bytes) -> int:
    """CRC-8 (poli 0x07)."""
    return crc_generico(dados, 8, 0x07, 0x00, False, 0x00)


def crc16_ccitt(dados: bytes) -> int:
    """CRC-16/CCITT-FALSE (poli 0x1021, init 0xFFFF)."""
    return crc_generico(dados, 16, 0x1021, 0xFFFF, False, 0x0000)


def crc32(dados: bytes) -> int:
    """CRC-32 (IEEE 802.3, o mesmo de zlib)."""
    return crc_generico(dados, 32, 0x04C11DB7, 0xFFFFFFFF, True, 0xFFFFFFFF)


def anexar_crc16(bloco: bytes) -> bytes:
    """Bloco seguido do CRC-16 em big-endian."""
    return bloco + crc16_ccitt(bloco).to_bytes(2, "big")


def verificar_crc16(quadro: bytes) -> bool:
    """True se o quadro (dados + CRC) está íntegro."""
    if len(quadro) < 2:
        return False
    return crc16_ccitt(quadro[:-2]) == int.from_bytes(quadro[-2:], "big")


def dividir_em_blocos(dados: bytes, tamanho: int) -> list[bytes]:
    if tamanho < 1:
        raise ValueError("tamanho deve ser >= 1")
    return [dados[i: i + tamanho] for i in range(0, len(dados), tamanho)]


def crcs_por_bloco(dados: bytes, tamanho: int) -> list[int]:
    """CRC-16 de cada bloco, para localizar o bloco corrompido."""
    return [crc16_ccitt(b) for b in dividir_em_blocos(dados, tamanho)]
