"""Lexer de Markdown: transforma texto em tokens de bloco e, dentro deles, tokens inline."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


class ErroMarkdown(Exception):
    """Markdown com estrutura inválida (ex.: bloco de código sem fechamento)."""


@dataclass
class TokenMd:
    tipo: str  # titulo, paragrafo, item, item_numerado, citacao, codigo, regra, vazio
    texto: str = ""
    nivel: int = 0
    linguagem: str = ""
    inline: list[tuple[str, str]] = field(default_factory=list)


_TITULO = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_ITEM = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_NUMERADO = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
_REGRA = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
_CERCA = re.compile(r"^(```|~~~)\s*([\w+-]*)\s*$")

_INLINE = re.compile(
    r"(?P<codigo>`[^`\n]+`)"
    r"|(?P<imagem>!\[[^\]]*\]\([^)\s]+\))"
    r"|(?P<link>\[[^\]]+\]\([^)\s]+\))"
    r"|(?P<negrito>\*\*[^*\n]+\*\*|__[^_\n]+__)"
    r"|(?P<italico>\*[^*\n]+\*|_[^_\n]+_)"
)


def tokens_inline(texto: str) -> list[tuple[str, str]]:
    """Divide um trecho em (tipo, conteúdo): texto, codigo, negrito, italico, link, imagem.

    Para link/imagem o conteúdo é 'rótulo|url'.
    """
    saida: list[tuple[str, str]] = []
    pos = 0
    for m in _INLINE.finditer(texto):
        if m.start() > pos:
            saida.append(("texto", texto[pos:m.start()]))
        tipo, bruto = m.lastgroup or "texto", m.group()
        if tipo == "codigo":
            conteudo = bruto[1:-1]
        elif tipo in ("negrito",):
            conteudo = bruto[2:-2]
        elif tipo == "italico":
            conteudo = bruto[1:-1]
        else:
            rotulo, _, url = bruto.lstrip("!")[1:-1].partition("](")
            conteudo = f"{rotulo}|{url}"
        saida.append((tipo, conteudo))
        pos = m.end()
    if pos < len(texto):
        saida.append(("texto", texto[pos:]))
    return saida


def tokenizar(texto: str) -> list[TokenMd]:
    """Lexer de blocos. Parágrafos consecutivos são unidos com espaço."""
    tokens: list[TokenMd] = []
    linhas = texto.splitlines()
    i = 0
    paragrafo: list[str] = []

    def fecha_paragrafo() -> None:
        if paragrafo:
            t = " ".join(paragrafo)
            tokens.append(TokenMd("paragrafo", t, inline=tokens_inline(t)))
            paragrafo.clear()

    while i < len(linhas):
        linha = linhas[i]
        cerca = _CERCA.match(linha.strip())
        if cerca:
            fecha_paragrafo()
            marca, lang = cerca.groups()
            corpo: list[str] = []
            i += 1
            while i < len(linhas) and linhas[i].strip() != marca:
                corpo.append(linhas[i])
                i += 1
            if i >= len(linhas):
                raise ErroMarkdown(f"bloco de código sem fechamento ({marca})")
            tokens.append(TokenMd("codigo", "\n".join(corpo), linguagem=lang))
            i += 1
            continue
        if not linha.strip():
            fecha_paragrafo()
            i += 1
            continue
        if m := _TITULO.match(linha):
            fecha_paragrafo()
            tokens.append(TokenMd("titulo", m.group(2), nivel=len(m.group(1)), inline=tokens_inline(m.group(2))))
        elif _REGRA.match(linha):
            fecha_paragrafo()
            tokens.append(TokenMd("regra"))
        elif m := _ITEM.match(linha):
            fecha_paragrafo()
            tokens.append(TokenMd("item", m.group(2), nivel=len(m.group(1)) // 2, inline=tokens_inline(m.group(2))))
        elif m := _NUMERADO.match(linha):
            fecha_paragrafo()
            tokens.append(TokenMd("item_numerado", m.group(3), nivel=len(m.group(1)) // 2,
                                  inline=tokens_inline(m.group(3))))
        elif linha.lstrip().startswith(">"):
            fecha_paragrafo()
            t = linha.lstrip()[1:].strip()
            tokens.append(TokenMd("citacao", t, inline=tokens_inline(t)))
        else:
            paragrafo.append(linha.strip())
        i += 1
    fecha_paragrafo()
    return tokens
