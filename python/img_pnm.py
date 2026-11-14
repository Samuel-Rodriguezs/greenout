"""Leitura e escrita de imagens PNM (PGM/PPM): P2/P3 em texto e P5/P6 binários.

Imagens em tons de cinza são listas de listas de inteiros; imagens RGB são
listas de listas de tuplas (r, g, b).
"""

Pixel = int | tuple[int, int, int]
Imagem = list[list[Pixel]]

_ESPACOS = b" \t\r\n\x0b\x0c"


def _token(dados: bytes, pos: int) -> tuple[bytes, int]:
    n = len(dados)
    while pos < n:
        if dados[pos] in _ESPACOS:
            pos += 1
        elif dados[pos] == 0x23:  # '#': comentário até o fim da linha
            while pos < n and dados[pos] != 0x0A:
                pos += 1
        else:
            break
    if pos >= n:
        raise ValueError("cabeçalho PNM incompleto")
    ini = pos
    while pos < n and dados[pos] not in _ESPACOS and dados[pos] != 0x23:
        pos += 1
    return dados[ini:pos], pos


def ler_pnm(dados: bytes) -> tuple[str, int, Imagem]:
    """Retorna (formato, valor_maximo, imagem)."""
    magia, pos = _token(dados, 0)
    formato = magia.decode("ascii", "replace")
    if formato not in ("P2", "P3", "P5", "P6"):
        raise ValueError(f"formato não suportado: {formato}")
    cab = []
    for _ in range(3):
        tok, pos = _token(dados, pos)
        cab.append(int(tok))
    larg, alt, maxval = cab
    if larg <= 0 or alt <= 0 or not 0 < maxval < 65536:
        raise ValueError("dimensões ou valor máximo inválidos")
    canais = 3 if formato in ("P3", "P6") else 1
    total = larg * alt * canais
    if formato in ("P2", "P3"):
        valores = []
        for _ in range(total):
            tok, pos = _token(dados, pos)
            valores.append(int(tok))
    else:
        pos += 1  # exatamente um espaço em branco após o valor máximo
        por = 2 if maxval > 255 else 1
        bruto = dados[pos:pos + total * por]
        if len(bruto) < total * por:
            raise ValueError("dados de pixels insuficientes")
        if por == 1:
            valores = list(bruto)
        else:
            valores = [(bruto[i] << 8) | bruto[i + 1] for i in range(0, len(bruto), 2)]
    if any(v > maxval for v in valores):
        raise ValueError("valor de pixel acima do máximo")
    imagem: Imagem = []
    for y in range(alt):
        linha: list[Pixel] = []
        for x in range(larg):
            i = (y * larg + x) * canais
            linha.append(valores[i] if canais == 1 else tuple(valores[i:i + 3]))
        imagem.append(linha)
    return formato, maxval, imagem


def escrever_pnm(imagem: Imagem, formato: str = "P5", maxval: int = 255) -> bytes:
    """Serializa a imagem no formato pedido (P2, P3, P5 ou P6)."""
    if formato not in ("P2", "P3", "P5", "P6"):
        raise ValueError(f"formato não suportado: {formato}")
    if not imagem or not imagem[0]:
        raise ValueError("imagem vazia")
    alt, larg = len(imagem), len(imagem[0])
    rgb = formato in ("P3", "P6")
    valores: list[int] = []
    for linha in imagem:
        if len(linha) != larg:
            raise ValueError("linhas com larguras diferentes")
        for p in linha:
            if rgb:
                if not isinstance(p, tuple) or len(p) != 3:
                    raise ValueError("formato RGB exige tuplas (r, g, b)")
                valores.extend(p)
            else:
                if isinstance(p, tuple):
                    raise ValueError("formato cinza exige inteiros")
                valores.append(p)
    if any(not 0 <= v <= maxval for v in valores):
        raise ValueError("valor de pixel fora de 0..maxval")
    cab = f"{formato}\n{larg} {alt}\n{maxval}\n".encode("ascii")
    if formato in ("P2", "P3"):
        passo = larg * (3 if rgb else 1)
        linhas = [" ".join(map(str, valores[i:i + passo])) for i in range(0, len(valores), passo)]
        return cab + "\n".join(linhas).encode("ascii") + b"\n"
    if maxval <= 255:
        return cab + bytes(valores)
    corpo = bytearray()
    for v in valores:
        corpo += bytes((v >> 8, v & 0xFF))
    return cab + bytes(corpo)
