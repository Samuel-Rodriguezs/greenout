"""Leitura e escrita de arquivos WAV PCM 16 bits (mono ou multicanal)."""
from __future__ import annotations

import struct
import wave

MAXIMO = 32767


def para_pcm16(amostras: list[float]) -> list[int]:
    """Converte floats em [-1, 1] para inteiros de 16 bits, com saturação."""
    saida = []
    for v in amostras:
        i = round(v * MAXIMO)
        saida.append(max(-MAXIMO - 1, min(MAXIMO, i)))
    return saida


def de_pcm16(inteiros: list[int]) -> list[float]:
    """Inteiros de 16 bits para floats em [-1, 1]."""
    return [max(-1.0, i / MAXIMO) for i in inteiros]


def escrever(caminho: str, amostras: list[float], taxa: int = 44100, canais: int = 1) -> None:
    """Grava amostras intercaladas (L R L R ...) como WAV PCM 16 bits."""
    if canais < 1:
        raise ValueError("canais deve ser >= 1")
    if taxa <= 0:
        raise ValueError("taxa deve ser positiva")
    if len(amostras) % canais:
        raise ValueError("número de amostras não é múltiplo de canais")
    inteiros = para_pcm16(amostras)
    with wave.open(caminho, "wb") as w:
        w.setnchannels(canais)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(struct.pack(f"<{len(inteiros)}h", *inteiros))


def ler(caminho: str) -> tuple[list[float], int, int]:
    """Retorna (amostras intercaladas, taxa, canais)."""
    with wave.open(caminho, "rb") as w:
        if w.getsampwidth() != 2:
            raise ValueError("somente PCM de 16 bits é suportado")
        canais = w.getnchannels()
        taxa = w.getframerate()
        bruto = w.readframes(w.getnframes())
    inteiros = struct.unpack(f"<{len(bruto) // 2}h", bruto)
    return de_pcm16(list(inteiros)), taxa, canais


def separar_canais(amostras: list[float], canais: int) -> list[list[float]]:
    """Desintercala em uma lista por canal."""
    if canais < 1:
        raise ValueError("canais deve ser >= 1")
    return [amostras[c::canais] for c in range(canais)]


def duracao(caminho: str) -> float:
    """Duração em segundos."""
    with wave.open(caminho, "rb") as w:
        return w.getnframes() / w.getframerate()
