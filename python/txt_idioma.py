"""Detector de idioma por frequência de letras (pt, en, es, fr, de, it)."""
import math
import unicodedata
from collections import Counter

# Frequências aproximadas (%) das letras mais comuns de cada idioma.
PERFIS: dict[str, dict[str, float]] = {
    "pt": dict(a=14.6, e=12.6, o=10.7, s=7.8, r=6.5, i=6.2, d=5.0, m=4.7, n=5.0, t=4.3, u=4.6, c=3.9, l=2.8),
    "en": dict(a=8.2, e=12.7, o=7.5, s=6.3, r=6.0, i=7.0, d=4.3, m=2.4, n=6.7, t=9.1, u=2.8, c=2.8, l=4.0, h=6.1),
    "es": dict(a=12.5, e=13.7, o=8.7, s=8.0, r=6.9, i=6.2, d=5.9, m=3.2, n=6.7, t=4.6, u=3.9, c=4.7, l=5.0),
    "fr": dict(a=7.6, e=14.7, o=5.4, s=7.9, r=6.6, i=7.5, d=3.7, m=2.7, n=7.1, t=7.2, u=6.3, c=3.3, l=5.5),
    "de": dict(a=6.5, e=16.4, o=2.5, s=7.3, r=7.0, i=7.6, d=5.1, m=2.5, n=9.8, t=6.2, u=4.2, c=3.1, l=3.4, h=4.8),
    "it": dict(a=11.7, e=11.8, o=9.8, s=5.0, r=6.4, i=11.3, d=3.7, m=2.5, n=6.9, t=5.6, u=3.0, c=4.5, l=6.5),
}


def _sem_acento(c: str) -> str:
    return unicodedata.normalize("NFD", c)[0]


def frequencias(texto: str) -> dict[str, float]:
    letras = [_sem_acento(c) for c in texto.lower() if c.isalpha()]
    letras = [c for c in letras if "a" <= c <= "z"]
    if not letras:
        return {}
    total = len(letras)
    return {c: 100 * n / total for c, n in Counter(letras).items()}


def pontuar(texto: str) -> dict[str, float]:
    """Distância euclidiana entre o texto e cada perfil (menor = mais parecido)."""
    freq = frequencias(texto)
    if not freq:
        raise ValueError("texto sem letras")
    return {
        lang: math.sqrt(sum((freq.get(c, 0.0) - perfil.get(c, 0.0)) ** 2 for c in set(freq) | set(perfil)))
        for lang, perfil in PERFIS.items()
    }


def detectar_idioma(texto: str) -> str:
    p = pontuar(texto)
    return min(sorted(p), key=lambda k: p[k])
