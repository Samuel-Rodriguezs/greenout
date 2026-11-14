"""Parser de arquivos .env (export, aspas, escapes, comentários e interpolação ${VAR})."""
from __future__ import annotations

import os
import re


class ErroDotenv(ValueError):
    """Linha .env inválida."""


_CHAVE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}


def _duplas(resto: str, n: int) -> tuple[str, str]:
    """Lê valor entre aspas duplas; retorna (valor, sobra)."""
    out: list[str] = []
    i = 1
    while i < len(resto):
        c = resto[i]
        if c == "\\" and i + 1 < len(resto):
            out.append(_ESCAPES.get(resto[i + 1], "\\" + resto[i + 1]))
            i += 2
            continue
        if c == '"':
            return "".join(out), resto[i + 1:]
        out.append(c)
        i += 1
    raise ErroDotenv(f"linha {n}: aspas duplas não fechadas")


def parse(texto: str, interpolar: bool = True, ambiente: dict[str, str] | None = None) -> dict[str, str]:
    """Interpreta o conteúdo; ${VAR} usa valores anteriores, depois `ambiente`."""
    res: dict[str, str] = {}
    amb = ambiente if ambiente is not None else dict(os.environ)
    linhas = texto.splitlines()
    idx = 0
    while idx < len(linhas):
        n = idx + 1
        linha = linhas[idx].strip()
        idx += 1
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith("export "):
            linha = linha[7:].lstrip()
        chave, igual, resto = linha.partition("=")
        chave = chave.strip()
        if not igual or not _CHAVE.fullmatch(chave):
            raise ErroDotenv(f"linha {n}: formato inválido: {linhas[n - 1]!r}")
        resto = resto.lstrip()
        expandir = True
        if resto.startswith('"'):
            # valores entre aspas duplas podem ocupar várias linhas
            while True:
                try:
                    valor, sobra = _duplas(resto, n)
                    break
                except ErroDotenv:
                    if idx >= len(linhas):
                        raise
                    resto += "\n" + linhas[idx]
                    idx += 1
        elif resto.startswith("'"):
            fim = resto.find("'", 1)
            if fim == -1:
                raise ErroDotenv(f"linha {n}: aspas simples não fechadas")
            valor, sobra, expandir = resto[1:fim], resto[fim + 1:], False
        else:
            m = re.search(r"\s+#", resto)
            valor, sobra = (resto[:m.start()] if m else resto).rstrip(), ""
        sobra = sobra.strip()
        if sobra and not sobra.startswith("#"):
            raise ErroDotenv(f"linha {n}: texto inesperado após o valor: {sobra!r}")
        if interpolar and expandir:
            valor = _expandir(valor, res, amb)
        res[chave] = valor
    return res


def _expandir(valor: str, atuais: dict[str, str], amb: dict[str, str]) -> str:
    def troca(m: re.Match[str]) -> str:
        if m.group(0) == "\\$":
            return "$"
        nome, _, padrao = (m.group(1) or m.group(2)).partition(":-")
        return atuais.get(nome) or amb.get(nome) or padrao
    return re.sub(r"\\\$|\$\{([^}]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)", troca, valor)


def serializar(dados: dict[str, str]) -> str:
    """Gera texto .env, usando aspas duplas quando necessário."""
    saida = []
    for k, v in dados.items():
        if not _CHAVE.fullmatch(k):
            raise ErroDotenv(f"chave inválida: {k!r}")
        if re.fullmatch(r"[A-Za-z0-9_./:@%+,-]*", v):
            saida.append(f"{k}={v}")
        else:
            esc = v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("$", "\\$")
            saida.append(f'{k}="{esc}"')
    return "\n".join(saida) + ("\n" if saida else "")
