"""Mini-interpretador de pilha: notação polonesa reversa."""
from typing import Callable, Dict, List


class ErroRPN(Exception):
    pass


def _div(a: float, b: float) -> float:
    if b == 0:
        raise ErroRPN("divisão por zero")
    return a / b


_BINARIOS: Dict[str, Callable[[float, float], float]] = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": _div,
    "^": lambda a, b: a ** b,
}


def avaliar_rpn(expressao: str) -> float:
    """Avalia 'a b +'. Comandos extras: dup, swap, drop."""
    pilha: List[float] = []

    def pop() -> float:
        if not pilha:
            raise ErroRPN("pilha vazia")
        return pilha.pop()

    for token in expressao.split():
        if token in _BINARIOS:
            b, a = pop(), pop()
            pilha.append(_BINARIOS[token](a, b))
        elif token == "dup":
            v = pop()
            pilha.extend([v, v])
        elif token == "swap":
            b, a = pop(), pop()
            pilha.extend([b, a])
        elif token == "drop":
            pop()
        else:
            try:
                pilha.append(float(token))
            except ValueError:
                raise ErroRPN(f"token inválido: {token}") from None
    if len(pilha) != 1:
        raise ErroRPN("expressão malformada")
    return pilha[0]
