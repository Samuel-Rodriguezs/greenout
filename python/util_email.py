import re

_PADRAO = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9._%+-]{0,62}[A-Za-z0-9])?"
    r"@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}$"
)


def validar_email(email: str) -> bool:
    """Valida um e-mail simples (usuario@dominio.tld) com regex."""
    if not isinstance(email, str) or len(email) > 254:
        return False
    if ".." in email:
        return False
    return _PADRAO.match(email) is not None


def dominio_do_email(email: str) -> str:
    """Retorna o domínio em minúsculas de um e-mail válido."""
    if not validar_email(email):
        raise ValueError(f"e-mail inválido: {email!r}")
    return email.rsplit("@", 1)[1].lower()
