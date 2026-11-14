"""Compressão sem perdas simples: LZ77 (janela deslizante) e LZW (dicionário)."""

Triplo = tuple[int, int, str]


def lz77_comprimir(texto: str, janela: int = 255, lookahead: int = 15) -> list[Triplo]:
    """Gera triplas (deslocamento, comprimento, próximo_caractere)."""
    if janela < 1 or lookahead < 1:
        raise ValueError("janela e lookahead devem ser >= 1")
    n = len(texto)
    saida: list[Triplo] = []
    i = 0
    while i < n:
        melhor_len, melhor_off = 0, 0
        for j in range(max(0, i - janela), i):
            k = 0
            while k < lookahead and i + k < n - 1 and texto[j + k] == texto[i + k]:
                k += 1
            if k > melhor_len:
                melhor_len, melhor_off = k, i - j
        saida.append((melhor_off, melhor_len, texto[i + melhor_len]))
        i += melhor_len + 1
    return saida


def lz77_descomprimir(triplas: list[Triplo]) -> str:
    saida: list[str] = []
    for off, comp, c in triplas:
        if comp > 0 and not 0 < off <= len(saida):
            raise ValueError("deslocamento inválido")
        for _ in range(comp):
            saida.append(saida[-off])
        saida.append(c)
    return "".join(saida)


def lzw_comprimir(texto: str) -> list[int]:
    """LZW sobre bytes UTF-8, com dicionário inicial de 256 entradas."""
    dic = {bytes([i]): i for i in range(256)}
    w = b""
    saida: list[int] = []
    for byte in texto.encode("utf-8"):
        wc = w + bytes([byte])
        if wc in dic:
            w = wc
        else:
            saida.append(dic[w])
            dic[wc] = len(dic)
            w = bytes([byte])
    if w:
        saida.append(dic[w])
    return saida


def lzw_descomprimir(codigos: list[int]) -> str:
    if not codigos:
        return ""
    dic = {i: bytes([i]) for i in range(256)}
    if not 0 <= codigos[0] < 256:
        raise ValueError("código inicial inválido")
    w = dic[codigos[0]]
    partes = [w]
    for k in codigos[1:]:
        if k in dic:
            entrada = dic[k]
        elif k == len(dic):
            entrada = w + w[:1]
        else:
            raise ValueError(f"código inválido: {k}")
        partes.append(entrada)
        dic[len(dic)] = w + entrada[:1]
        w = entrada
    return b"".join(partes).decode("utf-8")
