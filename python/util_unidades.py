def celsius_para_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32


def fahrenheit_para_celsius(f: float) -> float:
    return (f - 32) * 5 / 9


def celsius_para_kelvin(c: float) -> float:
    if c < -273.15:
        raise ValueError("abaixo do zero absoluto")
    return c + 273.15


_METROS = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
           "pol": 0.0254, "pe": 0.3048, "milha": 1609.344}


def converter_comprimento(valor: float, origem: str, destino: str) -> float:
    """Converte comprimentos entre mm, cm, m, km, pol, pe e milha."""
    for u in (origem, destino):
        if u not in _METROS:
            raise KeyError(f"unidade desconhecida: {u}")
    return valor * _METROS[origem] / _METROS[destino]
