"""Cifras clássicas: Vigenère, Atbash e código Morse."""
import unicodedata

MORSE: dict[str, str] = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.",
    "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.",
    "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-",
    "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--",
}
_MORSE_INV = {v: k for k, v in MORSE.items()}


def _vigenere(texto: str, chave: str, sinal: int) -> str:
    deslocs = [ord(c) - 97 for c in chave.lower() if "a" <= c <= "z"]
    if not deslocs or len(deslocs) != len(chave):
        raise ValueError("chave deve conter apenas letras a-z e não ser vazia")
    saida, k = [], 0
    for c in texto:
        if "a" <= c <= "z" or "A" <= c <= "Z":
            base = 97 if c.islower() else 65
            saida.append(chr((ord(c) - base + sinal * deslocs[k % len(deslocs)]) % 26 + base))
            k += 1
        else:
            saida.append(c)
    return "".join(saida)


def vigenere_cifrar(texto: str, chave: str) -> str:
    return _vigenere(texto, chave, 1)


def vigenere_decifrar(texto: str, chave: str) -> str:
    return _vigenere(texto, chave, -1)


def atbash(texto: str) -> str:
    """Espelha o alfabeto (a<->z); é sua própria inversa."""
    saida = []
    for c in texto:
        if "a" <= c <= "z":
            saida.append(chr(219 - ord(c)))
        elif "A" <= c <= "Z":
            saida.append(chr(155 - ord(c)))
        else:
            saida.append(c)
    return "".join(saida)


def morse_codificar(texto: str) -> str:
    """Letras separadas por espaço e palavras por ' / '. Acentos são removidos."""
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto.upper()) if not unicodedata.combining(c)
    )
    palavras = []
    for palavra in sem_acento.split():
        try:
            palavras.append(" ".join(MORSE[c] for c in palavra))
        except KeyError as e:
            raise ValueError(f"caractere sem código Morse: {e.args[0]!r}") from None
    return " / ".join(palavras)


def morse_decodificar(codigo: str) -> str:
    palavras = []
    for bloco in codigo.strip().split("/"):
        simbolos = bloco.split()
        try:
            palavras.append("".join(_MORSE_INV[s] for s in simbolos))
        except KeyError as e:
            raise ValueError(f"código Morse inválido: {e.args[0]!r}") from None
    return " ".join(p for p in palavras if p)
