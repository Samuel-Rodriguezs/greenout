"""String Calculator Kata."""
from __future__ import annotations

import re


def somar(entrada: str) -> int:
    """Soma números separados por vírgula/quebra de linha ou delimitador custom.

    - "//;\\n1;2" usa ';'; "//[***]\\n1***2" aceita delimitadores longos e
      múltiplos ("//[*][%]\\n1*2%3").
    - Números negativos lançam ValueError listando-os; > 1000 são ignorados.
    """
    if entrada == "":
        return 0
    delimitadores = [",", "\n"]
    corpo = entrada
    if entrada.startswith("//"):
        cabecalho, _, corpo = entrada[2:].partition("\n")
        longos = re.findall(r"\[(.+?)\]", cabecalho)
        delimitadores = longos if longos else [cabecalho]
    padrao = "|".join(re.escape(d) for d in delimitadores)
    numeros = [int(p) for p in re.split(padrao, corpo)]
    negativos = [n for n in numeros if n < 0]
    if negativos:
        raise ValueError("negativos não permitidos: " + ", ".join(map(str, negativos)))
    return sum(n for n in numeros if n <= 1000)
