"""Exaustividade e redundância de pattern matching (algoritmo de Maranget)."""
from __future__ import annotations

from tipos_algebricos import (PCon, PCoringa, PLit, PVar, Padrao, Universo,
                              ErroTipo)

Linha = list[Padrao]
Chave = tuple  # ("c", nome) ou ("l", tipo, valor)


def _norm(p: Padrao) -> Padrao:
    return PCoringa() if isinstance(p, PVar) else p


def _curinga(p: Padrao) -> bool:
    return isinstance(_norm(p), PCoringa)


def _chave(p: Padrao) -> Chave:
    if isinstance(p, PCon):
        return ("c", p.nome)
    assert isinstance(p, PLit)
    return ("l", type(p.valor).__name__, p.valor)


def _aridade(chave: Chave, u: Universo) -> int:
    if chave[0] == "l":
        return 0
    d = u.definicao_de(chave[1])
    return len(d.campos(chave[1]))


def _assinatura_completa(chaves: set[Chave], u: Universo) -> list[Chave] | None:
    """Todas as chaves do tipo, se `chaves` cobre o tipo inteiro; senão None."""
    if not chaves:
        return None
    exemplo = next(iter(chaves))
    if exemplo[0] == "l":
        if exemplo[1] == "bool" and {("l", "bool", True), ("l", "bool", False)} <= chaves:
            return [("l", "bool", True), ("l", "bool", False)]
        return None
    d = u.definicao_de(exemplo[1])
    todas = [("c", n) for n, _ in d.construtores]
    return todas if set(todas) <= chaves else None


def _especializar_linha(linha: Linha, chave: Chave, ar: int) -> Linha | None:
    cab = _norm(linha[0])
    if isinstance(cab, PCoringa):
        return [PCoringa()] * ar + linha[1:]
    if _chave(cab) != chave:
        return None
    subs = list(cab.subs) if isinstance(cab, PCon) else []
    if len(subs) != ar:
        raise ErroTipo(f"aridade incorreta em {chave[1]}")
    return subs + linha[1:]


def _especializar(m: list[Linha], chave: Chave, u: Universo) -> list[Linha]:
    ar = _aridade(chave, u)
    return [r for l in m if (r := _especializar_linha(l, chave, ar)) is not None]


def _default(m: list[Linha]) -> list[Linha]:
    return [l[1:] for l in m if _curinga(l[0])]


def _cabecas(m: list[Linha]) -> set[Chave]:
    return {_chave(_norm(l[0])) for l in m if not _curinga(l[0])}


def util(m: list[Linha], q: Linha, u: Universo) -> bool:
    """O vetor q casa algum valor que nenhuma linha de m casa?"""
    if not q:
        return not m
    cab = _norm(q[0])
    if not isinstance(cab, PCoringa):
        ch = _chave(cab)
        ar = _aridade(ch, u)
        subs = list(cab.subs) if isinstance(cab, PCon) else []
        if len(subs) != ar:
            raise ErroTipo(f"aridade incorreta em {ch[1]}")
        return util(_especializar(m, ch, u), subs + q[1:], u)
    completa = _assinatura_completa(_cabecas(m), u)
    if completa is not None:
        return any(
            util(_especializar(m, ch, u), [PCoringa()] * _aridade(ch, u) + q[1:], u)
            for ch in completa)
    return util(_default(m), q[1:], u)


def _construir(ch: Chave, subs: list[Padrao]) -> Padrao:
    if ch[0] == "l":
        return PLit(ch[2])
    return PCon(ch[1], tuple(subs))


def _testemunha(m: list[Linha], n: int, u: Universo) -> Linha | None:
    if n == 0:
        return [] if not m else None
    cabecas = _cabecas(m)
    completa = _assinatura_completa(cabecas, u)
    if completa is not None:
        for ch in completa:
            ar = _aridade(ch, u)
            r = _testemunha(_especializar(m, ch, u), ar + n - 1, u)
            if r is not None:
                return [_construir(ch, r[:ar])] + r[ar:]
        return None
    r = _testemunha(_default(m), n - 1, u)
    if r is None:
        return None
    if not cabecas:
        return [PCoringa()] + r
    return [_ausente(cabecas, u)] + r


def _ausente(cabecas: set[Chave], u: Universo) -> Padrao:
    exemplo = next(iter(cabecas))
    if exemplo[0] == "l":
        if exemplo[1] == "bool":
            falta = (True, False)[("l", "bool", True) in cabecas]
            return PLit(falta)
        usados = {c[2] for c in cabecas}
        k = 0
        while k in usados:
            k += 1
        return PLit(k)
    d = u.definicao_de(exemplo[1])
    for nome, campos in d.construtores:
        if ("c", nome) not in cabecas:
            return PCon(nome, tuple(PCoringa() for _ in campos))
    raise AssertionError("assinatura completa não deveria chegar aqui")


def exaustivo(padroes: list[Padrao], u: Universo) -> bool:
    return contra_exemplo(padroes, u) is None


def contra_exemplo(padroes: list[Padrao], u: Universo) -> Padrao | None:
    """Um padrão (valor) não coberto, ou None se o match é exaustivo."""
    r = _testemunha([[p] for p in padroes], 1, u)
    return None if r is None else r[0]


def redundantes(padroes: list[Padrao], u: Universo) -> list[int]:
    """Índices dos ramos que nunca são alcançados."""
    return [i for i, p in enumerate(padroes)
            if not util([[q] for q in padroes[:i]], [p], u)]


def mostrar_padrao(p: Padrao) -> str:
    if isinstance(p, PCoringa):
        return "_"
    if isinstance(p, PVar):
        return p.nome
    if isinstance(p, PLit):
        return repr(p.valor)
    if not p.subs:
        return p.nome
    return f"{p.nome}({', '.join(mostrar_padrao(s) for s in p.subs)})"
