"""Enquadramento HDLC: flag 0x7E, bit stuffing e FCS CRC-16/X.25."""
from __future__ import annotations

FLAG = [0, 1, 1, 1, 1, 1, 1, 0]  # 0x7E


def crc16_x25(dados: bytes) -> int:
    """CRC-16/X-25 (poly 0x1021 refletido, init 0xFFFF, xorout 0xFFFF)."""
    c = 0xFFFF
    for b in dados:
        c ^= b
        for _ in range(8):
            c = (c >> 1) ^ 0x8408 if c & 1 else c >> 1
    return c ^ 0xFFFF


def bytes_para_bits(dados: bytes) -> list[int]:
    """Bits na ordem de transmissão HDLC (LSB de cada byte primeiro)."""
    return [(b >> i) & 1 for b in dados for i in range(8)]


def bits_para_bytes(bits: list[int]) -> bytes:
    if len(bits) % 8:
        raise ValueError("número de bits não é múltiplo de 8")
    return bytes(sum(bits[i + j] << j for j in range(8)) for i in range(0, len(bits), 8))


def inserir_bits(bits: list[int]) -> list[int]:
    """Bit stuffing: após cinco 1s consecutivos insere um 0."""
    saida: list[int] = []
    uns = 0
    for b in bits:
        saida.append(b)
        uns = uns + 1 if b else 0
        if uns == 5:
            saida.append(0)
            uns = 0
    return saida


def remover_bits(bits: list[int]) -> list[int]:
    """Desfaz o stuffing; um sexto 1 consecutivo é erro (flag/abort)."""
    saida: list[int] = []
    uns = 0
    i = 0
    while i < len(bits):
        b = bits[i]
        if uns == 5:
            if b != 0:
                raise ValueError("sequência de 6 uns dentro do quadro")
            uns = 0
            i += 1
            continue
        saida.append(b)
        uns = uns + 1 if b else 0
        i += 1
    return saida


def montar_quadro(endereco: int, controle: int, dados: bytes) -> list[int]:
    """flag + stuffing(endereço, controle, dados, FCS) + flag, em bits."""
    corpo = bytes([endereco, controle]) + dados
    fcs = crc16_x25(corpo)
    corpo += bytes([fcs & 0xFF, fcs >> 8])  # FCS com o byte menos significativo primeiro
    return FLAG + inserir_bits(bytes_para_bits(corpo)) + FLAG


def extrair_quadros(fluxo: list[int]) -> list[tuple[int, int, bytes]]:
    """Procura flags no fluxo e devolve (endereço, controle, dados) dos quadros válidos."""
    quadros = []
    posicoes = [i for i in range(len(fluxo) - 7) if fluxo[i:i + 8] == FLAG]
    anterior = None
    for p in posicoes:
        if anterior is not None and p >= anterior + 8:
            miolo = fluxo[anterior + 8:p]
            if miolo:
                try:
                    corpo = bits_para_bytes(remover_bits(miolo))
                except ValueError:
                    corpo = b""
                if len(corpo) >= 4 and crc16_x25(corpo[:-2]) == corpo[-2] | (corpo[-1] << 8):
                    quadros.append((corpo[0], corpo[1], corpo[2:-2]))
        if anterior is None or p >= anterior + 8:
            anterior = p
    return quadros
