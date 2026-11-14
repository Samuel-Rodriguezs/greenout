"""Negociação de conteúdo a partir do cabeçalho Accept (e afins)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ItemAccept:
    valor: str
    q: float
    ordem: int


def parse_accept(cabecalho: str | None) -> list[ItemAccept]:
    """Ordena por q desc, depois especificidade (exato > tipo/* > */*), depois ordem de aparição."""
    if not cabecalho or not cabecalho.strip():
        return [ItemAccept("*/*", 1.0, 0)]
    itens: list[ItemAccept] = []
    for i, bloco in enumerate(cabecalho.split(",")):
        partes = [p.strip() for p in bloco.split(";")]
        valor = partes[0].lower()
        if not valor:
            continue
        q = 1.0
        for p in partes[1:]:
            if p.lower().startswith("q="):
                try:
                    q = float(p[2:])
                except ValueError:
                    raise ValueError(f"q inválido: {p}") from None
                if not 0 <= q <= 1:
                    raise ValueError(f"q fora de [0,1]: {q}")
        itens.append(ItemAccept(valor, q, i))

    def especificidade(it: ItemAccept) -> int:
        if it.valor == "*/*" or it.valor == "*":
            return 0
        return 1 if it.valor.endswith("/*") else 2

    return sorted(itens, key=lambda it: (-it.q, -especificidade(it), it.ordem))


def _casa(padrao: str, candidato: str) -> bool:
    if padrao in ("*/*", "*"):
        return True
    if padrao.endswith("/*"):
        return candidato.split("/")[0] == padrao[:-2]
    return padrao == candidato


def escolher(cabecalho: str | None, disponiveis: list[str]) -> str | None:
    """Melhor tipo oferecido pelo servidor; None se nada aceitável (responder 406).

    q=0 exclui explicitamente. A regra mais específica que casa define o q do candidato.
    """
    itens = parse_accept(cabecalho)
    melhor: tuple[float, int] | None = None
    escolhido: str | None = None
    for pos, cand in enumerate(disponiveis):
        aplicavel = None
        for it in itens:  # itens já estão do mais específico ao menos para o mesmo q
            if _casa(it.valor, cand.lower()):
                if aplicavel is None or _espec(it.valor) > _espec(aplicavel.valor):
                    aplicavel = it
        if aplicavel is None or aplicavel.q == 0:
            continue
        chave = (aplicavel.q, -pos)
        if melhor is None or chave > melhor:
            melhor, escolhido = chave, cand
    return escolhido


def _espec(v: str) -> int:
    return 0 if v in ("*/*", "*") else (1 if v.endswith("/*") else 2)


def escolher_idioma(cabecalho: str | None, disponiveis: list[str], padrao: str | None = None) -> str | None:
    """Accept-Language: casa 'pt-BR' com 'pt-br' exato ou prefixo 'pt'."""
    if not cabecalho:
        return padrao
    for it in parse_accept(cabecalho):
        if it.q == 0:
            continue
        v = it.valor
        if v in ("*", "*/*"):
            return disponiveis[0] if disponiveis else padrao
        for d in disponiveis:
            if d.lower() == v:
                return d
        base = v.split("-")[0]
        for d in disponiveis:
            if d.lower().split("-")[0] == base:
                return d
    return padrao
