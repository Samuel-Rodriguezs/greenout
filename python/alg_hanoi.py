"""Torre de Hanoi: sequência de movimentos."""


def hanoi(discos: int, origem: str = "A", auxiliar: str = "B", destino: str = "C") -> list[tuple[str, str]]:
    """Lista de movimentos (de, para) que move `discos` discos de origem a destino."""
    if discos < 0:
        raise ValueError("número de discos não pode ser negativo")
    movimentos: list[tuple[str, str]] = []

    def mover(n: int, a: str, b: str, c: str) -> None:
        if n == 0:
            return
        mover(n - 1, a, c, b)
        movimentos.append((a, c))
        mover(n - 1, b, a, c)

    mover(discos, origem, auxiliar, destino)
    return movimentos
