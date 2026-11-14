"""Conversor CSV <-> JSON em linha de comando."""
import argparse
import csv
import io
import json
import sys
from typing import Any, Dict, List, Optional, Sequence


def csv_para_json(texto: str, delimitador: str = ",") -> str:
    linhas = list(csv.DictReader(io.StringIO(texto), delimiter=delimitador))
    return json.dumps(linhas, ensure_ascii=False, indent=2)


def json_para_csv(texto: str, delimitador: str = ",") -> str:
    dados: List[Dict[str, Any]] = json.loads(texto)
    if not isinstance(dados, list) or not all(isinstance(d, dict) for d in dados):
        raise ValueError("JSON deve ser uma lista de objetos")
    campos: List[str] = []
    for d in dados:
        for k in d:
            if k not in campos:
                campos.append(k)
    saida = io.StringIO()
    w = csv.DictWriter(saida, fieldnames=campos, delimiter=delimitador, lineterminator="\n")
    w.writeheader()
    w.writerows(dados)
    return saida.getvalue()


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Converte entre CSV e JSON (pela extensão do arquivo de entrada).")
    p.add_argument("entrada")
    p.add_argument("-o", "--saida", help="arquivo de saída (padrão: stdout)")
    p.add_argument("-d", "--delimitador", default=",")
    a = p.parse_args(argv)
    try:
        with open(a.entrada, encoding="utf-8", newline="") as f:
            texto = f.read()
        if a.entrada.lower().endswith(".json"):
            resultado = json_para_csv(texto, a.delimitador)
        else:
            resultado = csv_para_json(texto, a.delimitador)
    except (OSError, ValueError) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    if a.saida:
        with open(a.saida, "w", encoding="utf-8", newline="") as f:
            f.write(resultado)
    else:
        sys.stdout.write(resultado if resultado.endswith("\n") else resultado + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
