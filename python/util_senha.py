import secrets
import string

SIMBOLOS = "!@#$%^&*()-_=+"


def gerar_senha(tamanho: int = 16, simbolos: bool = True) -> str:
    """Gera senha aleatória com `secrets`, garantindo ao menos um de cada classe."""
    grupos = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if simbolos:
        grupos.append(SIMBOLOS)
    if tamanho < len(grupos):
        raise ValueError(f"tamanho mínimo é {len(grupos)}")
    if tamanho > 1024:
        raise ValueError("tamanho máximo é 1024")
    todos = "".join(grupos)
    caracteres = [secrets.choice(g) for g in grupos]
    caracteres += [secrets.choice(todos) for _ in range(tamanho - len(grupos))]
    secrets.SystemRandom().shuffle(caracteres)
    return "".join(caracteres)
