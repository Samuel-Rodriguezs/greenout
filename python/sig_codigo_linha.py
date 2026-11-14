"""Codificação de linha: NRZ-L, Manchester (IEEE 802.3) e AMI, com decodificação."""
from __future__ import annotations


def _validar_bits(bits: list[int]) -> None:
    if any(b not in (0, 1) for b in bits):
        raise ValueError("bits devem ser 0 ou 1")


def nrz_codificar(bits: list[int]) -> list[int]:
    """NRZ-L: 1 -> +1, 0 -> -1."""
    _validar_bits(bits)
    return [1 if b else -1 for b in bits]


def nrz_decodificar(niveis: list[int]) -> list[int]:
    return [1 if v > 0 else 0 for v in niveis]


def manchester_codificar(bits: list[int]) -> list[int]:
    """IEEE 802.3: 0 -> (+1, -1) e 1 -> (-1, +1); dois níveis por bit."""
    _validar_bits(bits)
    saida: list[int] = []
    for b in bits:
        saida += [-1, 1] if b else [1, -1]
    return saida


def manchester_decodificar(niveis: list[int]) -> list[int]:
    if len(niveis) % 2:
        raise ValueError("quantidade de níveis deve ser par")
    bits = []
    for i in range(0, len(niveis), 2):
        par = (niveis[i] > 0, niveis[i + 1] > 0)
        if par == (False, True):
            bits.append(1)
        elif par == (True, False):
            bits.append(0)
        else:
            raise ValueError(f"violação de Manchester na posição {i}")
    return bits


def ami_codificar(bits: list[int]) -> list[int]:
    """AMI: 0 -> 0 e 1 alterna entre +1 e -1."""
    _validar_bits(bits)
    saida = []
    polaridade = 1
    for b in bits:
        if b:
            saida.append(polaridade)
            polaridade = -polaridade
        else:
            saida.append(0)
    return saida


def ami_decodificar(niveis: list[int]) -> list[int]:
    """Verifica a alternância de polaridade dos pulsos; viola -> ValueError."""
    bits = []
    ultima = -1
    for i, v in enumerate(niveis):
        if v == 0:
            bits.append(0)
        elif v in (1, -1):
            if v == ultima:
                raise ValueError(f"violação bipolar na posição {i}")
            ultima = v
            bits.append(1)
        else:
            raise ValueError("níveis AMI devem ser -1, 0 ou 1")
    return bits


def para_forma_de_onda(niveis: list[int], amostras_por_simbolo: int) -> list[float]:
    """Repete cada nível para gerar uma forma de onda retangular."""
    if amostras_por_simbolo < 1:
        raise ValueError("amostras_por_simbolo deve ser >= 1")
    return [float(v) for v in niveis for _ in range(amostras_por_simbolo)]


def transicoes(niveis: list[int]) -> int:
    """Número de mudanças de nível (relevante para recuperação de clock)."""
    return sum(1 for a, b in zip(niveis, niveis[1:]) if a != b)
