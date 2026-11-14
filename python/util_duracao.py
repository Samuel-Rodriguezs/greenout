import re


def formatar_duracao(segundos: int | float) -> str:
    """Formata segundos como '1h 02min 05s' (omite unidades zeradas à esquerda)."""
    if isinstance(segundos, bool) or not isinstance(segundos, (int, float)):
        raise TypeError("segundos deve ser numérico")
    if segundos < 0:
        raise ValueError("duração não pode ser negativa")
    total = int(segundos)
    h, resto = divmod(total, 3600)
    m, s = divmod(resto, 60)
    if h:
        return f"{h}h {m:02d}min {s:02d}s"
    if m:
        return f"{m}min {s:02d}s"
    return f"{s}s"


_PADRAO = re.compile(r"^\s*(?:(\d+)h)?\s*(?:(\d+)min)?\s*(?:(\d+)s)?\s*$")


def interpretar_duracao(texto: str) -> int:
    """Inverso de formatar_duracao: '1h 02min 05s' -> 3725."""
    m = _PADRAO.match(texto)
    if not m or not any(m.groups()):
        raise ValueError(f"duração inválida: {texto!r}")
    h, mi, s = (int(g) if g else 0 for g in m.groups())
    return h * 3600 + mi * 60 + s
