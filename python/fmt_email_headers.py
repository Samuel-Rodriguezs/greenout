"""Parser de cabeçalhos de e-mail (RFC 822 simplificado)."""
from __future__ import annotations

import re
from dataclasses import dataclass


class ErroEmail(ValueError):
    """Mensagem de e-mail malformada."""


@dataclass(frozen=True)
class Endereco:
    nome: str
    email: str


def parse_cabecalhos(texto: str) -> tuple[dict[str, list[str]], str]:
    """Retorna (cabeçalhos com nomes em minúsculas -> lista de valores, corpo)."""
    texto = texto.replace("\r\n", "\n")
    cab_txt, sep, corpo = texto.partition("\n\n")
    if not sep and texto.endswith("\n"):
        cab_txt = texto.rstrip("\n")
    cab: dict[str, list[str]] = {}
    ultimo: tuple[str, int] | None = None
    for linha in cab_txt.split("\n"):
        if not linha:
            continue
        if linha[0] in " \t":
            if ultimo is None:
                raise ErroEmail("linha de continuação sem cabeçalho")
            nome, idx = ultimo
            cab[nome][idx] += " " + linha.strip()
            continue
        nome, dp, valor = linha.partition(":")
        if not dp or not re.fullmatch(r"[!-9;-~]+", nome):
            raise ErroEmail(f"cabeçalho inválido: {linha!r}")
        nome = nome.lower()
        cab.setdefault(nome, []).append(valor.strip())
        ultimo = (nome, len(cab[nome]) - 1)
    if not cab:
        raise ErroEmail("nenhum cabeçalho encontrado")
    return cab, corpo


def _dividir_enderecos(valor: str) -> list[str]:
    partes, atual, aspas, ang = [], [], False, 0
    for c in valor:
        if c == '"':
            aspas = not aspas
        elif not aspas and c == "<":
            ang += 1
        elif not aspas and c == ">":
            ang -= 1
        if c == "," and not aspas and ang == 0:
            partes.append("".join(atual))
            atual = []
        else:
            atual.append(c)
    if aspas or ang != 0:
        raise ErroEmail(f"endereço mal formado: {valor!r}")
    partes.append("".join(atual))
    return [p.strip() for p in partes if p.strip()]


def parse_enderecos(valor: str) -> list[Endereco]:
    """Interpreta 'Nome <a@b>, c@d, "X, Y" <e@f>' em uma lista de Endereco."""
    res: list[Endereco] = []
    for p in _dividir_enderecos(valor):
        m = re.fullmatch(r'(?:"((?:[^"\\]|\\.)*)"|([^<]*?))\s*<([^<>]*)>', p)
        if m:
            nome = (m.group(1) if m.group(1) is not None else m.group(2)).strip()
            nome = re.sub(r"\\(.)", r"\1", nome)
            email = m.group(3).strip()
        else:
            nome, email = "", re.sub(r"\([^)]*\)", "", p).strip()
        if not re.fullmatch(r"[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+|[^@\s<>]+@localhost", email):
            raise ErroEmail(f"endereço inválido: {p!r}")
        res.append(Endereco(nome, email))
    return res


def decodificar_palavra(valor: str) -> str:
    """Decodifica palavras codificadas RFC 2047 (=?utf-8?B?...?= e =?...?Q?...?=)."""
    import base64

    def troca(m: re.Match[str]) -> str:
        cs, enc, dados = m.group(1), m.group(2).upper(), m.group(3)
        try:
            if enc == "B":
                return base64.b64decode(dados).decode(cs)
            q = dados.replace("_", " ")
            bruto = re.sub(r"=([0-9A-Fa-f]{2})", lambda x: chr(int(x.group(1), 16)), q)
            return bruto.encode("latin-1").decode(cs)
        except (ValueError, LookupError) as e:
            raise ErroEmail(f"palavra codificada inválida: {m.group(0)!r}") from e
    sem_espaco = re.sub(r"(\?=)\s+(=\?)", r"\1\2", valor)
    return re.sub(r"=\?([\w\-]+)\?([BbQq])\?([^?]*)\?=", troca, sem_espaco)
