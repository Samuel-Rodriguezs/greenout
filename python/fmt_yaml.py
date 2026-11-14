"""Parser de um subconjunto de YAML: mapas, listas e escalares."""
from __future__ import annotations

from typing import Any


class ErroYaml(ValueError):
    """Erro de sintaxe no documento YAML."""


def _escalar(texto: str) -> Any:
    t = texto.strip()
    if t == "" or t in ("~", "null", "Null", "NULL"):
        return None
    if t in ("true", "True", "TRUE"):
        return True
    if t in ("false", "False", "FALSE"):
        return False
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        corpo = t[1:-1]
        if t[0] == '"':
            return (corpo.replace('\\n', '\n').replace('\\t', '\t')
                    .replace('\\"', '"').replace('\\\\', '\\'))
        return corpo.replace("''", "'")
    if t[0] in "\"'":
        raise ErroYaml(f"string não terminada: {t}")
    if t.startswith("[") or t.startswith("{"):
        return _fluxo(t)
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        return t


def _dividir_fluxo(corpo: str) -> list[str]:
    partes: list[str] = []
    atual: list[str] = []
    prof = 0
    aspas = ""
    for c in corpo:
        if aspas:
            atual.append(c)
            if c == aspas:
                aspas = ""
            continue
        if c in "\"'":
            aspas = c
        elif c in "[{":
            prof += 1
        elif c in "]}":
            prof -= 1
        elif c == "," and prof == 0:
            partes.append("".join(atual))
            atual = []
            continue
        atual.append(c)
    if aspas or prof != 0:
        raise ErroYaml("coleção inline mal formada")
    resto = "".join(atual)
    if resto.strip():
        partes.append(resto)
    return partes


def _fluxo(t: str) -> Any:
    if t[0] == "[":
        if t[-1] != "]":
            raise ErroYaml(f"lista inline não fechada: {t}")
        return [_escalar(p) for p in _dividir_fluxo(t[1:-1])]
    if t[-1] != "}":
        raise ErroYaml(f"mapa inline não fechado: {t}")
    mapa: dict[str, Any] = {}
    for p in _dividir_fluxo(t[1:-1]):
        chave, sep, valor = p.partition(":")
        if not sep:
            raise ErroYaml(f"par inválido: {p}")
        mapa[str(_escalar(chave))] = _escalar(valor)
    return mapa


def _tirar_comentario(linha: str) -> str:
    aspas = ""
    for i, c in enumerate(linha):
        if aspas:
            if c == aspas:
                aspas = ""
        elif c in "\"'":
            aspas = c
        elif c == "#" and (i == 0 or linha[i - 1] in " \t"):
            return linha[:i]
    return linha


def _separar_chave(conteudo: str) -> tuple[str, str] | None:
    aspas = ""
    for i, c in enumerate(conteudo):
        if aspas:
            if c == aspas:
                aspas = ""
        elif c in "\"'":
            aspas = c
        elif c == ":" and (i + 1 == len(conteudo) or conteudo[i + 1] == " "):
            return conteudo[:i].strip(), conteudo[i + 1:].strip()
    return None


class _Parser:
    def __init__(self, texto: str) -> None:
        self.linhas: list[tuple[int, str]] = []
        for bruta in texto.splitlines():
            if "\t" in bruta[: len(bruta) - len(bruta.lstrip())]:
                raise ErroYaml("tabulação na indentação")
            limpa = _tirar_comentario(bruta).rstrip()
            if not limpa.strip() or limpa.strip() == "---":
                continue
            self.linhas.append((len(limpa) - len(limpa.lstrip()), limpa.strip()))
        self.pos = 0

    def bloco(self, indent: int) -> Any:
        ind, cont = self.linhas[self.pos]
        if ind != indent:
            raise ErroYaml(f"indentação inesperada: {cont}")
        if cont == "-" or cont.startswith("- "):
            return self.lista(indent)
        return self.mapa(indent)

    def valor_apos(self, resto: str, indent: int) -> Any:
        if resto:
            return _escalar(resto)
        if self.pos < len(self.linhas):
            prox_ind, prox = self.linhas[self.pos]
            if prox_ind > indent or (prox_ind == indent and prox.startswith("-")):
                return self.bloco(prox_ind)
        return None

    def mapa(self, indent: int) -> dict[str, Any]:
        res: dict[str, Any] = {}
        while self.pos < len(self.linhas):
            ind, cont = self.linhas[self.pos]
            if ind < indent:
                break
            if ind > indent:
                raise ErroYaml(f"indentação inesperada: {cont}")
            if cont.startswith("- ") or cont == "-":
                break
            par = _separar_chave(cont)
            if par is None:
                raise ErroYaml(f"esperado 'chave: valor': {cont}")
            chave, resto = par
            chave = str(_escalar(chave))
            if chave in res:
                raise ErroYaml(f"chave duplicada: {chave}")
            self.pos += 1
            res[chave] = self.valor_apos(resto, indent)
        return res

    def lista(self, indent: int) -> list[Any]:
        res: list[Any] = []
        while self.pos < len(self.linhas):
            ind, cont = self.linhas[self.pos]
            if ind < indent:
                break
            if ind > indent:
                raise ErroYaml(f"indentação inesperada: {cont}")
            if not (cont == "-" or cont.startswith("- ")):
                break
            resto = cont[1:].strip()
            par = _separar_chave(resto) if resto and resto[0] not in "[{\"'" else None
            if par is not None:
                # item é um mapa cujo primeiro par está na linha do traço
                novo_ind = indent + 2
                self.linhas[self.pos] = (novo_ind, resto)
                res.append(self.mapa(novo_ind))
            else:
                self.pos += 1
                res.append(self.valor_apos(resto, indent))
        return res


def carregar(texto: str) -> Any:
    """Converte texto YAML (subconjunto) em estruturas Python."""
    p = _Parser(texto)
    if not p.linhas:
        return None
    ind, cont = p.linhas[0]
    if ind == 0 and not cont.startswith("-") and _separar_chave(cont) is None:
        if len(p.linhas) > 1:
            raise ErroYaml("escalar seguido de conteúdo extra")
        return _escalar(cont)
    resultado = p.bloco(ind)
    if p.pos < len(p.linhas):
        raise ErroYaml(f"conteúdo inesperado: {p.linhas[p.pos][1]}")
    return resultado


def _numerico(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _fmt_escalar(v: Any) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if (s == "" or s != s.strip() or s[0] in "-[]{}#&*!|>'\"%@`" or ": " in s or " #" in s
            or s.endswith(":") or s.lower() in ("null", "true", "false", "~") or _numerico(s)):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return s


def _inline(v: Any) -> str:
    if isinstance(v, dict):
        return "{}"
    if isinstance(v, list):
        return "[]"
    return _fmt_escalar(v)


def serializar(valor: Any, indent: int = 0) -> str:
    """Serializa estruturas Python no mesmo subconjunto de YAML."""
    pad = " " * indent
    linhas: list[str] = []
    if isinstance(valor, dict):
        if not valor:
            return pad + "{}"
        for k, v in valor.items():
            if isinstance(v, (dict, list)) and v:
                linhas.append(f"{pad}{k}:")
                linhas.append(serializar(v, indent + 2))
            else:
                linhas.append(f"{pad}{k}: {_inline(v)}")
    elif isinstance(valor, list):
        if not valor:
            return pad + "[]"
        for v in valor:
            if isinstance(v, (dict, list)) and v:
                sub = serializar(v, indent + 2).split("\n")
                linhas.append(f"{pad}- {sub[0].lstrip()}")
                linhas.extend(sub[1:])
            else:
                linhas.append(f"{pad}- {_inline(v)}")
    else:
        return pad + _fmt_escalar(valor)
    return "\n".join(linhas)
