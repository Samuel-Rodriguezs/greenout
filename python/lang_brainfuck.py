"""Interpretador de Brainfuck com fita de bytes (células de 8 bits, com wrap)."""
from __future__ import annotations


class ErroBrainfuck(Exception):
    """Erro de sintaxe ou execução em um programa Brainfuck."""


def _mapear_colchetes(programa: str) -> dict[int, int]:
    pares: dict[int, int] = {}
    pilha: list[int] = []
    for i, c in enumerate(programa):
        if c == "[":
            pilha.append(i)
        elif c == "]":
            if not pilha:
                raise ErroBrainfuck(f"']' sem '[' na posição {i}")
            j = pilha.pop()
            pares[i] = j
            pares[j] = i
    if pilha:
        raise ErroBrainfuck(f"'[' sem ']' na posição {pilha[-1]}")
    return pares


def executar(programa: str, entrada: str = "", tamanho_fita: int = 30000,
             max_passos: int = 10_000_000) -> str:
    """Executa o programa e devolve a saída como texto."""
    pares = _mapear_colchetes(programa)
    fita = [0] * tamanho_fita
    ptr = 0
    pc = 0
    ent = list(entrada.encode("utf-8"))
    pos_ent = 0
    saida = bytearray()
    passos = 0
    while pc < len(programa):
        passos += 1
        if passos > max_passos:
            raise ErroBrainfuck("limite de passos excedido")
        c = programa[pc]
        if c == ">":
            ptr += 1
            if ptr >= tamanho_fita:
                raise ErroBrainfuck("ponteiro além do fim da fita")
        elif c == "<":
            ptr -= 1
            if ptr < 0:
                raise ErroBrainfuck("ponteiro antes do início da fita")
        elif c == "+":
            fita[ptr] = (fita[ptr] + 1) % 256
        elif c == "-":
            fita[ptr] = (fita[ptr] - 1) % 256
        elif c == ".":
            saida.append(fita[ptr])
        elif c == ",":
            if pos_ent < len(ent):
                fita[ptr] = ent[pos_ent]
                pos_ent += 1
            else:
                fita[ptr] = 0
        elif c == "[":
            if fita[ptr] == 0:
                pc = pares[pc]
        elif c == "]":
            if fita[ptr] != 0:
                pc = pares[pc]
        pc += 1
    return saida.decode("utf-8", errors="replace")
