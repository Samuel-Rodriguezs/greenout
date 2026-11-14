import re
from collections import Counter


def contar_palavras(texto: str) -> Counter:
    return Counter(re.findall(r"\w+", texto.lower()))
