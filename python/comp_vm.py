"""Máquina virtual de pilha própria para Mini: conjunto de instruções e interpretador.

Modelo: cada função tem um vetor de locais (parâmetros primeiro) e um código
linear com saltos absolutos (índice da instrução). Valores são int ou bool na
pilha de operandos, compartilhada entre chamadas. ``CALL f`` consome os
argumentos da pilha (o primeiro argumento é o mais fundo) e toda função deixa
exatamente um valor na pilha ao retornar (``0`` para funções void). A função
principal termina com ``HALT``.

Instruções::

    PUSH v      empilha constante        LOAD i / STORE i   local i
    ADD SUB MUL DIV MOD NEG NOT          EQ NE LT LE GT GE
    JMP a       salta                    JZ a  desempilha; salta se falso
    DUP / POP   duplica / descarta topo  CALL f  chama função de índice f
    RET         retorna topo             PRINT   imprime e descarta
    HALT        encerra o programa
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from comp_folding import aplicar_binario, aplicar_unario
from comp_lexer import ErroMini


class Op(Enum):
    PUSH = "PUSH"
    LOAD = "LOAD"
    STORE = "STORE"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    NEG = "NEG"
    NOT = "NOT"
    EQ = "EQ"
    NE = "NE"
    LT = "LT"
    LE = "LE"
    GT = "GT"
    GE = "GE"
    JMP = "JMP"
    JZ = "JZ"
    DUP = "DUP"
    POP = "POP"
    CALL = "CALL"
    RET = "RET"
    PRINT = "PRINT"
    HALT = "HALT"


OP_BINARIO = {
    Op.ADD: "+", Op.SUB: "-", Op.MUL: "*", Op.DIV: "/", Op.MOD: "%",
    Op.EQ: "==", Op.NE: "!=", Op.LT: "<", Op.LE: "<=", Op.GT: ">", Op.GE: ">=",
}
OP_UNARIO = {Op.NEG: "-", Op.NOT: "!"}
COM_ARGUMENTO = {Op.PUSH, Op.LOAD, Op.STORE, Op.JMP, Op.JZ, Op.CALL}


class ErroExecucao(ErroMini):
    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem, 0, 0)


@dataclass(frozen=True)
class Instr:
    op: Op
    arg: Any = None

    def __str__(self) -> str:
        if self.op in COM_ARGUMENTO:
            arg = str(self.arg).lower() if isinstance(self.arg, bool) else self.arg
            return f"{self.op.value} {arg}"
        return self.op.value


@dataclass
class FuncaoVM:
    nome: str
    n_params: int
    n_locais: int
    codigo: list[Instr] = field(default_factory=list)


@dataclass
class ProgramaVM:
    funcoes: list[FuncaoVM]
    principal: FuncaoVM
    nomes_principal: dict[str, int] = field(default_factory=dict)


@dataclass
class ResultadoVM:
    saida: list[str]
    locais: list[Any]
    passos: int


def desmontar(programa: ProgramaVM) -> str:
    """Listagem textual do bytecode (uma instrução por linha, com índices)."""
    linhas: list[str] = []
    for f in [programa.principal] + programa.funcoes:
        linhas.append(f"{f.nome}  (params={f.n_params}, locais={f.n_locais}):")
        for i, ins in enumerate(f.codigo):
            linhas.append(f"  {i:3d}  {ins}")
    return "\n".join(linhas)


def formatar_valor(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def executar(programa: ProgramaVM, max_passos: int = 10_000_000,
             max_profundidade: int = 1000,
             locais_iniciais: Optional[dict[int, Any]] = None) -> ResultadoVM:
    """Executa o programa. ``locais_iniciais`` preenche slots da função principal."""
    saida: list[str] = []
    pilha: list[Any] = []
    principal = programa.principal
    locais = [0] * principal.n_locais
    for slot, v in (locais_iniciais or {}).items():
        locais[slot] = v
    # quadro: (função, pc, locais); o quadro atual fica em variáveis locais
    quadros: list[tuple[FuncaoVM, int, list[Any]]] = []
    func, pc, passos = principal, 0, 0

    def desempilhar() -> Any:
        if not pilha:
            raise ErroExecucao(f"pilha vazia em {func.nome}:{pc - 1}")
        return pilha.pop()

    while True:
        if pc >= len(func.codigo):
            raise ErroExecucao(f"execução saiu do fim de '{func.nome}'")
        ins = func.codigo[pc]
        pc += 1
        passos += 1
        if passos > max_passos:
            raise ErroExecucao("limite de passos excedido")
        op = ins.op
        if op is Op.PUSH:
            pilha.append(ins.arg)
        elif op is Op.LOAD:
            pilha.append(locais[ins.arg])
        elif op is Op.STORE:
            locais[ins.arg] = desempilhar()
        elif op in OP_BINARIO:
            b, a = desempilhar(), desempilhar()
            try:
                pilha.append(aplicar_binario(OP_BINARIO[op], a, b))
            except ZeroDivisionError:
                raise ErroExecucao("divisão por zero") from None
        elif op in OP_UNARIO:
            pilha.append(aplicar_unario(OP_UNARIO[op], desempilhar()))
        elif op is Op.JMP:
            pc = ins.arg
        elif op is Op.JZ:
            if not desempilhar():
                pc = ins.arg
        elif op is Op.DUP:
            v = desempilhar()
            pilha.extend((v, v))
        elif op is Op.POP:
            desempilhar()
        elif op is Op.CALL:
            if len(quadros) >= max_profundidade:
                raise ErroExecucao("estouro da pilha de chamadas")
            alvo = programa.funcoes[ins.arg]
            args = [desempilhar() for _ in range(alvo.n_params)][::-1]
            quadros.append((func, pc, locais))
            func, pc = alvo, 0
            locais = args + [0] * (alvo.n_locais - alvo.n_params)
        elif op is Op.RET:
            if not quadros:
                raise ErroExecucao("RET fora de chamada")
            func, pc, locais = quadros.pop()
        elif op is Op.PRINT:
            saida.append(formatar_valor(desempilhar()))
        elif op is Op.HALT:
            return ResultadoVM(saida, locais, passos)
        else:  # pragma: no cover
            raise ErroExecucao(f"instrução desconhecida {op}")
