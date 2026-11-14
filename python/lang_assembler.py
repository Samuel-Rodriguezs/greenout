"""Assembler textual para a VM de pilha (lang_vm), com rótulos e comentários."""
from __future__ import annotations

from lang_vm import COM_ARGUMENTO, OPCODES, Instrucao

SALTOS = {"JMP", "JZ", "JNZ", "CALL"}


class ErroAssembler(Exception):
    """Erro de sintaxe no código assembly."""


def montar(fonte: str) -> list[Instrucao]:
    """Converte assembly em lista de instruções da VM.

    Sintaxe: `rotulo:`, `MNEMONICO [arg]`, comentários com `;`.
    """
    linhas: list[tuple[int, list[str]]] = []
    rotulos: dict[str, int] = {}
    for n, bruta in enumerate(fonte.splitlines(), 1):
        linha = bruta.split(";", 1)[0].strip()
        while ":" in linha:
            nome, linha = (s.strip() for s in linha.split(":", 1))
            if not nome.isidentifier():
                raise ErroAssembler(f"linha {n}: rótulo inválido {nome!r}")
            if nome in rotulos:
                raise ErroAssembler(f"linha {n}: rótulo duplicado {nome!r}")
            rotulos[nome] = len(linhas)
        if linha:
            linhas.append((n, linha.split()))

    programa: list[Instrucao] = []
    for n, partes in linhas:
        mn = partes[0].upper()
        if mn not in OPCODES:
            raise ErroAssembler(f"linha {n}: instrução desconhecida {partes[0]!r}")
        op = OPCODES[mn]
        if op in COM_ARGUMENTO:
            if len(partes) != 2:
                raise ErroAssembler(f"linha {n}: {mn} requer 1 argumento")
            arg = partes[1]
            if mn in SALTOS:
                if arg.isdigit():
                    programa.append((op, int(arg)))
                elif arg in rotulos:
                    programa.append((op, rotulos[arg]))
                else:
                    raise ErroAssembler(f"linha {n}: rótulo indefinido {arg!r}")
            else:
                try:
                    programa.append((op, int(arg)))
                except ValueError:
                    raise ErroAssembler(f"linha {n}: argumento inválido {arg!r}") from None
        else:
            if len(partes) != 1:
                raise ErroAssembler(f"linha {n}: {mn} não aceita argumento")
            programa.append((op, None))
    return programa


def desmontar(programa: list[Instrucao]) -> str:
    """Gera assembly (com endereços numéricos nos saltos não rotulados)."""
    nomes = {v: k for k, v in OPCODES.items()}
    return "\n".join(
        nomes[op] if arg is None else f"{nomes[op]} {arg}" for op, arg in programa
    )
