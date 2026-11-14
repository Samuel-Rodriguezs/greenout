from collections import Counter


def sao_anagramas(a: str, b: str) -> bool:
    def norm(t):
        return Counter(c.lower() for c in t if c.isalnum())
    return norm(a) == norm(b)
