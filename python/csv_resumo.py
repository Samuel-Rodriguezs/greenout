import csv
from io import StringIO


def media_por_coluna(texto_csv: str) -> dict[str, float]:
    """Média de cada coluna numérica de um CSV com cabeçalho."""
    leitor = csv.DictReader(StringIO(texto_csv))
    somas, qtd = {}, {}
    for linha in leitor:
        for k, v in linha.items():
            try:
                x = float(v)
            except (TypeError, ValueError):
                continue
            somas[k] = somas.get(k, 0.0) + x
            qtd[k] = qtd.get(k, 0) + 1
    return {k: somas[k] / qtd[k] for k in somas}
