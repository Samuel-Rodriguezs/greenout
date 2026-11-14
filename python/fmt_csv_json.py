"""Conversor CSV -> JSON em streaming, com parser CSV (RFC 4180) e serializador JSON próprios."""
from __future__ import annotations

from typing import Iterable, Iterator


class ErroCsv(ValueError):
    """CSV malformado."""


def ler_registros(pedacos: Iterable[str], separador: str = ",") -> Iterator[list[str]]:
    """Gera registros (listas de campos) a partir de pedaços arbitrários de texto."""
    campo: list[str] = []
    registro: list[str] = []
    aspas = False
    apos_aspas = False  # acabou de fechar um campo entre aspas
    iniciado = False
    anterior_cr = False
    for pedaco in pedacos:
        for c in pedaco:
            if anterior_cr:
                anterior_cr = False
                if c == "\n":
                    continue
            if aspas:
                if c == '"':
                    aspas, apos_aspas = False, True
                else:
                    campo.append(c)
                continue
            if apos_aspas and c == '"':
                campo.append('"')
                aspas, apos_aspas = True, False
                continue
            if c == separador:
                registro.append("".join(campo))
                campo, apos_aspas, iniciado = [], False, True
            elif c in "\r\n":
                anterior_cr = c == "\r"
                if iniciado or campo or registro or apos_aspas:
                    registro.append("".join(campo))
                    yield registro
                registro, campo, apos_aspas, iniciado = [], [], False, False
            elif c == '"' and not campo and not apos_aspas:
                aspas, iniciado = True, True
            elif apos_aspas:
                raise ErroCsv("texto após aspas de fechamento")
            else:
                campo.append(c)
                iniciado = True
    if aspas:
        raise ErroCsv("aspas não fechadas no fim da entrada")
    if iniciado or campo or registro or apos_aspas:
        registro.append("".join(campo))
        yield registro


_ESC = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t", "\b": "\\b", "\f": "\\f"}


def json_string(s: str) -> str:
    return '"' + "".join(_ESC.get(c) or (f"\\u{ord(c):04x}" if ord(c) < 0x20 else c) for c in s) + '"'


def _valor(s: str, inferir: bool) -> str:
    if not inferir:
        return json_string(s)
    t = s.strip()
    if t == "":
        return "null"
    if t in ("true", "false"):
        return t
    try:
        int(t)
        if t.lstrip("-").isdigit() and not (len(t.lstrip("-")) > 1 and t.lstrip("-")[0] == "0"):
            return str(int(t))
    except ValueError:
        pass
    try:
        f = float(t)
        if t[-1].isdigit() and "inf" not in t.lower() and "nan" not in t.lower() and t[0] != "+" \
                and "_" not in t and not (t.lstrip("-").startswith("0") and not t.lstrip("-").startswith("0.")):
            return repr(f)
    except ValueError:
        pass
    return json_string(s)


def converter(pedacos: Iterable[str], separador: str = ",", inferir_tipos: bool = True,
              cabecalho: bool = True) -> Iterator[str]:
    """Gera o JSON (array) aos poucos: '[', cada objeto/array, ']' — sem manter tudo em memória."""
    nomes: list[str] | None = None
    primeiro = True
    n = 0
    yield "["
    for reg in ler_registros(pedacos, separador):
        n += 1
        if cabecalho and nomes is None:
            if len(set(reg)) != len(reg):
                raise ErroCsv("cabeçalho com colunas duplicadas")
            nomes = reg
            continue
        if nomes is not None and len(reg) != len(nomes):
            raise ErroCsv(f"registro {n} tem {len(reg)} campos, esperado {len(nomes)}")
        vals = [_valor(v, inferir_tipos) for v in reg]
        corpo = ("{" + ",".join(f"{json_string(k)}:{v}" for k, v in zip(nomes, vals)) + "}") if nomes is not None \
            else "[" + ",".join(vals) + "]"
        yield ("" if primeiro else ",") + corpo
        primeiro = False
    yield "]"


def csv_para_json(texto: str, **kw: object) -> str:
    return "".join(converter([texto], **kw))  # type: ignore[arg-type]
