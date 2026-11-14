"""Janela deslizante simulada: Go-Back-N e Selective Repeat.

A simulação é determinística: um conjunto `perdas` indica quais transmissões
de quadros (por número de sequência, na 1ª vez em que são enviados) se perdem.
"""
from __future__ import annotations


def go_back_n(total: int, janela: int, perdas: set[int] | None = None) -> list[int]:
    """Devolve a ordem de todas as transmissões feitas até entregar `total` quadros.

    Perda de um quadro (apenas na 1ª tentativa): o receptor descarta os
    seguintes, o timeout estoura e o remetente retransmite desde a base.
    """
    if total < 0 or janela < 1:
        raise ValueError("total >= 0 e janela >= 1")
    perdas = set(perdas or ())
    perdidos_ja = set()
    base, envios = 0, []
    while base < total:
        fim = min(base + janela, total)
        esperado = base
        for seq in range(base, fim):
            envios.append(seq)
            if seq in perdas and seq not in perdidos_ja:
                perdidos_ja.add(seq)
                continue  # perdido
            if seq == esperado:
                esperado += 1  # receptor aceita somente em ordem
        base = esperado  # ACKs cumulativos fazem a janela avançar até aqui
    return envios


def selective_repeat(total: int, janela: int, perdas: set[int] | None = None) -> list[int]:
    """Retransmite somente os quadros perdidos; receptor armazena fora de ordem."""
    if total < 0 or janela < 1:
        raise ValueError("total >= 0 e janela >= 1")
    perdas = set(perdas or ())
    confirmados: set[int] = set()
    base, envios = 0, []
    ja_enviou: set[int] = set()
    while base < total:
        fim = min(base + janela, total)
        for seq in range(base, fim):
            if seq in confirmados:
                continue
            envios.append(seq)
            if seq in perdas and seq not in ja_enviou:
                ja_enviou.add(seq)
                continue
            ja_enviou.add(seq)
            confirmados.add(seq)
        while base in confirmados:
            base += 1
    return envios


def eficiencia(total: int, envios: list[int]) -> float:
    """Quadros úteis / transmissões feitas."""
    if not envios:
        return 1.0
    return total / len(envios)


def janela_maxima_valida(bits_seq: int, protocolo: str) -> int:
    """Maior janela sem ambiguidade: GBN = 2^n - 1, SR = 2^(n-1)."""
    if bits_seq < 1:
        raise ValueError("bits_seq >= 1")
    if protocolo == "gbn":
        return (1 << bits_seq) - 1
    if protocolo == "sr":
        return 1 << (bits_seq - 1)
    raise ValueError("protocolo deve ser 'gbn' ou 'sr'")
