"""Rock-Paper-Scissors-Lizard-Spock Kata."""
from __future__ import annotations

# jogada -> {jogada derrotada: verbo}
REGRAS: dict[str, dict[str, str]] = {
    "tesoura": {"papel": "corta", "lagarto": "decapita"},
    "papel": {"pedra": "embrulha", "spock": "refuta"},
    "pedra": {"lagarto": "esmaga", "tesoura": "quebra"},
    "lagarto": {"spock": "envenena", "papel": "come"},
    "spock": {"tesoura": "esmaga", "pedra": "vaporiza"},
}


def jogar(a: str, b: str) -> str:
    """Retorna 'empate', 'jogador 1' ou 'jogador 2'."""
    a, b = a.lower(), b.lower()
    for j in (a, b):
        if j not in REGRAS:
            raise ValueError(f"jogada inválida: {j}")
    if a == b:
        return "empate"
    return "jogador 1" if b in REGRAS[a] else "jogador 2"


def descricao(a: str, b: str) -> str:
    """Explica o resultado, ex.: 'tesoura corta papel'."""
    a, b = a.lower(), b.lower()
    resultado = jogar(a, b)
    if resultado == "empate":
        return f"{a} empata com {b}"
    vencedor, perdedor = (a, b) if resultado == "jogador 1" else (b, a)
    return f"{vencedor} {REGRAS[vencedor][perdedor]} {perdedor}"
