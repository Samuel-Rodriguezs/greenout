def fizzbuzz(n: int) -> list[str]:
    """Retorna a sequência FizzBuzz de 1 até n."""
    saida = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            saida.append("FizzBuzz")
        elif i % 3 == 0:
            saida.append("Fizz")
        elif i % 5 == 0:
            saida.append("Buzz")
        else:
            saida.append(str(i))
    return saida
