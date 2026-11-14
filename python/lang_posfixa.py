"""Conversão infixa -> posfixa (shunting-yard) e avaliação de expressões posfixas."""
from __future__ import annotations

import re

_TOKEN = re.compile(r"\s*(\d+(?:\.\d+)?|[A-Za-z_]\w*|[-+*/^%()])")

# operador -> (precedência, associativa à direita)
_OPS: dict[str, tuple[int, bool]] = {
    "+": (1, False), "-": (1, False),
    "*": (2, False), "/": (2, False), "%": (2, False),
    "^": (3, True),
}
_UNARIO = "u-"  # menos unário, precedência acima de * e abaixo de ^


class ErroExpressao(Exception):
    """Expressão mal formada."""


def tokenizar(expr: str) -> list[str]:
    tokens, pos = [], 0
    while pos < len(expr):
        if expr[pos:].strip() == "":
            break
        m = _TOKEN.match(expr, pos)
        if not m:
            raise ErroExpressao(f"caractere inesperado {expr[pos:].lstrip()[0]!r}")
        tokens.append(m.group(1))
        pos = m.end()
    return tokens


def infixa_para_posfixa(expr: str) -> list[str]:
    """Devolve a lista de tokens em notação posfixa. `-` unário vira `u-`."""
    saida: list[str] = []
    pilha: list[str] = []
    esperando_operando = True
    for tok in tokenizar(expr):
        if tok[0].isalnum() or tok[0] == "_":
            if not esperando_operando:
                raise ErroExpressao(f"operador esperado antes de {tok!r}")
            saida.append(tok)
            esperando_operando = False
        elif tok == "(":
            if not esperando_operando:
                raise ErroExpressao("operador esperado antes de '('")
            pilha.append(tok)
        elif tok == ")":
            if esperando_operando:
                raise ErroExpressao("operando esperado antes de ')'")
            while pilha and pilha[-1] != "(":
                saida.append(pilha.pop())
            if not pilha:
                raise ErroExpressao("')' sem '(' correspondente")
            pilha.pop()
        elif esperando_operando:
            if tok == "-":
                pilha.append(_UNARIO)
            elif tok == "+":
                continue
            else:
                raise ErroExpressao(f"operando esperado, encontrado {tok!r}")
        else:
            prec, direita = _OPS[tok]
            while pilha and pilha[-1] != "(":
                topo = pilha[-1]
                p_topo = 2.5 if topo == _UNARIO else _OPS[topo][0]
                if p_topo > prec or (p_topo == prec and not direita):
                    saida.append(pilha.pop())
                else:
                    break
            pilha.append(tok)
            esperando_operando = True
    if esperando_operando:
        raise ErroExpressao("expressão incompleta")
    while pilha:
        op = pilha.pop()
        if op == "(":
            raise ErroExpressao("'(' não fechado")
        saida.append(op)
    return saida


def avaliar_posfixa(tokens: list[str], variaveis: dict[str, float] | None = None) -> float:
    variaveis = variaveis or {}
    pilha: list[float] = []
    for tok in tokens:
        if tok == _UNARIO:
            if not pilha:
                raise ErroExpressao("operandos insuficientes")
            pilha.append(-pilha.pop())
        elif tok in _OPS:
            if len(pilha) < 2:
                raise ErroExpressao("operandos insuficientes")
            b, a = pilha.pop(), pilha.pop()
            if tok == "+":
                pilha.append(a + b)
            elif tok == "-":
                pilha.append(a - b)
            elif tok == "*":
                pilha.append(a * b)
            elif tok == "^":
                pilha.append(a ** b)
            else:
                if b == 0:
                    raise ErroExpressao("divisão por zero")
                pilha.append(a / b if tok == "/" else a % b)
        elif tok[0].isdigit():
            pilha.append(float(tok))
        elif tok in variaveis:
            pilha.append(variaveis[tok])
        else:
            raise ErroExpressao(f"variável indefinida: {tok}")
    if len(pilha) != 1:
        raise ErroExpressao("expressão posfixa inválida")
    return pilha[0]


def avaliar(expr: str, variaveis: dict[str, float] | None = None) -> float:
    return avaliar_posfixa(infixa_para_posfixa(expr), variaveis)
