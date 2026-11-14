def fibonacci(n: int) -> list[int]:
    """Retorna os n primeiros números de Fibonacci."""
    if n < 0:
        raise ValueError("n deve ser >= 0")
    seq, a, b = [], 0, 1
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq
