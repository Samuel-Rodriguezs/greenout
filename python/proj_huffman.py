"""Codificador de Huffman (tabela de codigos, codificar e decodificar)."""
import heapq
from collections import Counter
from typing import Dict, List, Tuple, Union

No = Union[str, Tuple["No", "No"]]


def construir_codigos(texto: str) -> Dict[str, str]:
    if not texto:
        raise ValueError("texto vazio")
    freq = Counter(texto)
    # (frequencia, desempate, no) garante ordem deterministica
    heap: List[Tuple[int, int, No]] = [(f, i, c) for i, (c, f) in enumerate(sorted(freq.items()))]
    heapq.heapify(heap)
    if len(heap) == 1:
        return {heap[0][2]: "0"}  # type: ignore[dict-item]
    contador = len(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, contador, (a, b)))
        contador += 1
    codigos: Dict[str, str] = {}

    def percorrer(no: No, prefixo: str) -> None:
        if isinstance(no, str):
            codigos[no] = prefixo
        else:
            percorrer(no[0], prefixo + "0")
            percorrer(no[1], prefixo + "1")

    percorrer(heap[0][2], "")
    return codigos


def codificar(texto: str, codigos: Dict[str, str]) -> str:
    try:
        return "".join(codigos[c] for c in texto)
    except KeyError as e:
        raise ValueError(f"simbolo sem codigo: {e.args[0]!r}") from None


def decodificar(bits: str, codigos: Dict[str, str]) -> str:
    inverso = {v: k for k, v in codigos.items()}
    saida, atual = [], ""
    for b in bits:
        if b not in "01":
            raise ValueError("bit invalido")
        atual += b
        if atual in inverso:
            saida.append(inverso[atual])
            atual = ""
    if atual:
        raise ValueError("sequencia de bits incompleta")
    return "".join(saida)
