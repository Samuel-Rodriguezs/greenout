"""Cifra de César: desloca letras do alfabeto, preservando maiúsculas e demais caracteres."""


def cifrar_cesar(texto: str, deslocamento: int) -> str:
    """Cifra o texto deslocando cada letra ASCII; aceita deslocamento negativo ou maior que 26."""
    resultado = []
    for caractere in texto:
        if "a" <= caractere <= "z":
            base = ord("a")
        elif "A" <= caractere <= "Z":
            base = ord("A")
        else:
            resultado.append(caractere)
            continue
        resultado.append(chr((ord(caractere) - base + deslocamento) % 26 + base))
    return "".join(resultado)


def decifrar_cesar(texto: str, deslocamento: int) -> str:
    """Desfaz a cifra de César aplicada com o mesmo deslocamento."""
    return cifrar_cesar(texto, -deslocamento)
