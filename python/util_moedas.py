from decimal import ROUND_HALF_UP, Decimal

# Cotações em BRL por 1 unidade da moeda (valores fixos de exemplo).
TAXAS_BRL: dict[str, Decimal] = {
    "BRL": Decimal("1"),
    "USD": Decimal("5.00"),
    "EUR": Decimal("5.50"),
    "GBP": Decimal("6.40"),
}


def converter(valor: float | str | Decimal, origem: str, destino: str,
              taxas: dict[str, Decimal] | None = None) -> Decimal:
    """Converte valor entre moedas via BRL, arredondando a 2 casas."""
    taxas = taxas if taxas is not None else TAXAS_BRL
    origem, destino = origem.upper(), destino.upper()
    for moeda in (origem, destino):
        if moeda not in taxas:
            raise KeyError(f"moeda não suportada: {moeda}")
    valor = Decimal(str(valor))
    if valor < 0:
        raise ValueError("valor não pode ser negativo")
    em_brl = valor * taxas[origem]
    return (em_brl / taxas[destino]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
