"""Modelos de procuração com substituição de campos {{campo}} e verificação de pendências."""
from __future__ import annotations

import re

_CAMPO = re.compile(r"\{\{\s*([a-z_][a-z0-9_]*)\s*\}\}")

MODELO_AD_JUDICIA = (
    "PROCURAÇÃO AD JUDICIA\n"
    "OUTORGANTE: {{outorgante}}, {{documento}}, residente em {{endereco}}.\n"
    "OUTORGADO: {{advogado}}, OAB/{{uf}} {{oab}}.\n"
    "PODERES: foro em geral, {{poderes}}.\n"
    "{{cidade}}, {{data}}."
)


def campos_do_modelo(modelo: str) -> list[str]:
    """Nomes de campos na ordem de primeira aparição, sem repetição."""
    vistos: list[str] = []
    for m in _CAMPO.finditer(modelo):
        if m.group(1) not in vistos:
            vistos.append(m.group(1))
    return vistos


def campos_faltantes(modelo: str, valores: dict[str, str]) -> list[str]:
    return [c for c in campos_do_modelo(modelo) if not str(valores.get(c, "")).strip()]


def preencher(modelo: str, valores: dict[str, str], estrito: bool = True) -> str:
    """Substitui os campos. Em modo estrito, campo sem valor levanta ValueError."""
    faltam = campos_faltantes(modelo, valores)
    if faltam and estrito:
        raise ValueError("campos sem valor: " + ", ".join(faltam))
    return _CAMPO.sub(lambda m: str(valores.get(m.group(1), m.group(0))).strip() or m.group(0), modelo)


def preencher_com_poderes_especiais(modelo: str, valores: dict[str, str], especiais: list[str]) -> str:
    """Acrescenta poderes especiais (receber, transigir...) ao campo `poderes`."""
    v = dict(valores)
    base = v.get("poderes", "").strip()
    extras = ", ".join(e.strip() for e in especiais if e.strip())
    v["poderes" ] = ", ".join(x for x in (base, extras) if x) or "poderes gerais"
    return preencher(modelo, v)
