"""Driver do compilador Mini: encadeia todas as etapas do pipeline.

    fonte -> tokens -> AST -> semântica -> tipos -> [otimizações]
          -> { VM de pilha | Python | TAC | TAC com registradores } -> saída

``frontend`` reúne os erros de todas as análises; ``otimizar`` repete
propagação, dobramento, simplificação e eliminação de código morto até a
árvore estabilizar; ``executar`` roda por qualquer um dos backends.
"""
from __future__ import annotations

from comp_algebra import simplificar
from comp_ast import Programa
from comp_blocos import construir_cfg
from comp_codigo_morto import eliminar_codigo_morto
from comp_folding import dobrar_constantes
from comp_gerador import gerar
from comp_lexer import ErroMini
from comp_parser import parse
from comp_propagacao import propagar_constantes
from comp_regalloc import alocar, renomear
from comp_semantica import analisar
from comp_tac import ProgramaTAC, executar_tac, gerar_tac
from comp_tipos import verificar
from comp_transpilador import executar_python
from comp_vm import executar as executar_vm

BACKENDS = ("vm", "python", "tac", "tac_regs")


class ErroCompilacao(Exception):
    """Agrupa os erros (léxico/sintático, semânticos ou de tipo) de um fonte."""

    def __init__(self, erros: list[ErroMini]) -> None:
        super().__init__("; ".join(str(e) for e in erros))
        self.erros = erros


def frontend(fonte: str) -> Programa:
    """Analisa e valida o fonte; levanta ErroCompilacao com todos os erros."""
    try:
        programa = parse(fonte)
    except ErroMini as e:  # léxico/sintático: a análise não continua
        raise ErroCompilacao([e]) from e
    erros: list[ErroMini] = list(analisar(programa).erros)
    if not erros:  # tipos só fazem sentido com nomes resolvidos
        erros.extend(verificar(programa))
    if erros:
        raise ErroCompilacao(erros)
    return programa


def otimizar(programa: Programa, max_rodadas: int = 20) -> Programa:
    atual = programa
    for _ in range(max_rodadas):
        novo = eliminar_codigo_morto(simplificar(dobrar_constantes(propagar_constantes(atual))))
        if novo == atual:
            break
        atual = novo
    return atual


def _executar_tac_com_registradores(programa: Programa, k: int) -> list[str]:
    tac = gerar_tac(programa)
    novas = []
    for f in tac.funcoes + [tac.principal]:
        aloc, _ = alocar(f.codigo, k, f.params)
        novas.append(renomear(f, aloc))
    return executar_tac(ProgramaTAC(novas[:-1], novas[-1]))


def executar_programa(programa: Programa, backend: str = "vm", k: int = 3) -> list[str]:
    if backend == "vm":
        return executar_vm(gerar(programa)).saida
    if backend == "python":
        return executar_python(programa)
    if backend == "tac":
        return executar_tac(gerar_tac(programa))
    if backend == "tac_regs":
        return _executar_tac_com_registradores(programa, k)
    raise ValueError(f"backend desconhecido: {backend} (use {', '.join(BACKENDS)})")


def executar(fonte: str, backend: str = "vm", otimizado: bool = False) -> list[str]:
    """Compila e executa um programa Mini, devolvendo as linhas impressas."""
    programa = frontend(fonte)
    if otimizado:
        programa = otimizar(programa)
    return executar_programa(programa, backend)


def blocos_da_principal(programa: Programa) -> int:
    """Quantidade de blocos básicos do código principal (métrica de otimização)."""
    return len(construir_cfg(gerar_tac(programa).principal.codigo).blocos)
