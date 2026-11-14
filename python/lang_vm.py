"""Máquina virtual de pilha com bytecode simples.

Instruções são tuplas (opcode, argumento opcional). Opcodes numéricos em OPCODES.
"""
from __future__ import annotations

from typing import Sequence

PUSH, POP, ADD, SUB, MUL, DIV, MOD = range(7)
DUP, SWAP, EQ, LT, GT, JMP, JZ, JNZ = range(7, 15)
LOAD, STORE, PRINT, CALL, RET, HALT = range(15, 21)

OPCODES: dict[str, int] = {
    "PUSH": PUSH, "POP": POP, "ADD": ADD, "SUB": SUB, "MUL": MUL, "DIV": DIV,
    "MOD": MOD, "DUP": DUP, "SWAP": SWAP, "EQ": EQ, "LT": LT, "GT": GT,
    "JMP": JMP, "JZ": JZ, "JNZ": JNZ, "LOAD": LOAD, "STORE": STORE,
    "PRINT": PRINT, "CALL": CALL, "RET": RET, "HALT": HALT,
}
COM_ARGUMENTO = {PUSH, JMP, JZ, JNZ, LOAD, STORE, CALL}

Instrucao = tuple[int, int | None]


class ErroVM(Exception):
    """Erro de execução da máquina virtual."""


class VM:
    def __init__(self, programa: Sequence[Instrucao], max_passos: int = 1_000_000) -> None:
        self.programa = list(programa)
        self.pilha: list[int] = []
        self.chamadas: list[int] = []
        self.memoria: dict[int, int] = {}
        self.saida: list[int] = []
        self.pc = 0
        self.max_passos = max_passos

    def _pop(self) -> int:
        if not self.pilha:
            raise ErroVM(f"pilha vazia em pc={self.pc}")
        return self.pilha.pop()

    def _arg(self, arg: int | None) -> int:
        if arg is None:
            raise ErroVM(f"instrução sem argumento em pc={self.pc}")
        return arg

    def executar(self) -> list[int]:
        passos = 0
        while self.pc < len(self.programa):
            passos += 1
            if passos > self.max_passos:
                raise ErroVM("limite de passos excedido")
            op, arg = self.programa[self.pc]
            self.pc += 1
            if op == PUSH:
                self.pilha.append(self._arg(arg))
            elif op == POP:
                self._pop()
            elif op in (ADD, SUB, MUL, DIV, MOD, EQ, LT, GT):
                b, a = self._pop(), self._pop()
                if op == ADD:
                    r = a + b
                elif op == SUB:
                    r = a - b
                elif op == MUL:
                    r = a * b
                elif op in (DIV, MOD):
                    if b == 0:
                        raise ErroVM("divisão por zero")
                    r = a // b if op == DIV else a % b
                elif op == EQ:
                    r = int(a == b)
                elif op == LT:
                    r = int(a < b)
                else:
                    r = int(a > b)
                self.pilha.append(r)
            elif op == DUP:
                v = self._pop()
                self.pilha += [v, v]
            elif op == SWAP:
                b, a = self._pop(), self._pop()
                self.pilha += [b, a]
            elif op == JMP:
                self.pc = self._destino(arg)
            elif op == JZ:
                if self._pop() == 0:
                    self.pc = self._destino(arg)
            elif op == JNZ:
                if self._pop() != 0:
                    self.pc = self._destino(arg)
            elif op == LOAD:
                self.pilha.append(self.memoria.get(self._arg(arg), 0))
            elif op == STORE:
                self.memoria[self._arg(arg)] = self._pop()
            elif op == PRINT:
                self.saida.append(self._pop())
            elif op == CALL:
                self.chamadas.append(self.pc)
                self.pc = self._destino(arg)
            elif op == RET:
                if not self.chamadas:
                    raise ErroVM("RET sem CALL")
                self.pc = self.chamadas.pop()
            elif op == HALT:
                break
            else:
                raise ErroVM(f"opcode inválido: {op}")
        return self.saida

    def _destino(self, arg: int | None) -> int:
        d = self._arg(arg)
        if not 0 <= d <= len(self.programa):
            raise ErroVM(f"destino de salto inválido: {d}")
        return d


def executar(programa: Sequence[Instrucao]) -> list[int]:
    """Executa o programa e devolve os valores impressos."""
    return VM(programa).executar()
