"""Strings geradas por gramática: expansão recursiva de templates com marcadores {nome}."""
from __future__ import annotations

import random
import re

_MARCADOR = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

Gramatica = dict[str, list[str]]


def validar(gramatica: Gramatica, inicio: str) -> None:
    """Levanta ValueError se faltar regra, houver regra vazia ou recursão sem saída."""
    if inicio not in gramatica:
        raise ValueError(f"símbolo inicial sem regra: {inicio!r}")
    for nome, alternativas in gramatica.items():
        if not alternativas:
            raise ValueError(f"regra vazia: {nome!r}")
        for alt in alternativas:
            for ref in _MARCADOR.findall(alt):
                if ref not in gramatica:
                    raise ValueError(f"regra {nome!r} referencia {ref!r} inexistente")
    # toda regra precisa ter ao menos uma derivação finita
    terminaveis: set[str] = set()
    mudou = True
    while mudou:
        mudou = False
        for nome, alternativas in gramatica.items():
            if nome in terminaveis:
                continue
            if any(all(r in terminaveis for r in _MARCADOR.findall(a)) for a in alternativas):
                terminaveis.add(nome)
                mudou = True
    nao = set(gramatica) - terminaveis
    if nao:
        raise ValueError(f"regras sem derivação finita: {sorted(nao)}")


def _alturas_minimas(gramatica: Gramatica) -> dict[str, int]:
    """Menor altura de derivação de cada símbolo (terminal puro = 0); ponto fixo."""
    inf = float("inf")
    alt: dict[str, float] = {n: inf for n in gramatica}
    mudou = True
    while mudou:
        mudou = False
        for nome, alternativas in gramatica.items():
            for a in alternativas:
                refs = _MARCADOR.findall(a)
                h = 0 if not refs else 1 + max(alt[r] for r in refs)
                if h < alt[nome]:
                    alt[nome] = h
                    mudou = True
    return {n: int(h) for n, h in alt.items()}


def expandir(
    rng: random.Random, gramatica: Gramatica, inicio: str = "inicio", profundidade_max: int = 20
) -> str:
    """Expande `inicio`; ao passar de `profundidade_max` só usa as alternativas de menor altura
    de derivação, garantindo que a expansão termina."""
    validar(gramatica, inicio)
    minimas = _alturas_minimas(gramatica)

    def altura(a: str) -> int:
        refs = _MARCADOR.findall(a)
        return 0 if not refs else 1 + max(minimas[r] for r in refs)

    def rec(simbolo: str, prof: int) -> str:
        alts = gramatica[simbolo]
        if prof >= profundidade_max:
            melhor = min(altura(a) for a in alts)
            alts = [a for a in alts if altura(a) == melhor]
        escolha = rng.choice(alts)
        return _MARCADOR.sub(lambda m: rec(m.group(1), prof + 1), escolha)

    return rec(inicio, 0)


def gerar_lote(seed: int, gramatica: Gramatica, n: int, inicio: str = "inicio") -> list[str]:
    rng = random.Random(seed)
    return [expandir(rng, gramatica, inicio) for _ in range(n)]


def preencher(template: str, valores: dict[str, str]) -> str:
    """Substitui {chave} por valores[chave]; chave ausente é erro."""
    def troca(m: re.Match[str]) -> str:
        if m.group(1) not in valores:
            raise KeyError(m.group(1))
        return valores[m.group(1)]

    return _MARCADOR.sub(troca, template)


GRAMATICA_SAUDACOES: Gramatica = {
    "inicio": ["{saudacao}, {pessoa}! {pedido}", "{saudacao}, {pessoa}."],
    "saudacao": ["Olá", "Bom dia", "Boa tarde", "Oi"],
    "pessoa": ["{titulo} {sobrenome}", "{titulo} {sobrenome} {sobrenome}"],
    "titulo": ["dona", "seu", "doutora", "professor"],
    "sobrenome": ["Silva", "Lima", "Costa", "Rocha"],
    "pedido": ["Pode conferir o {objeto}?", "Falta enviar o {objeto}, e também o {objeto}."],
    "objeto": ["relatório", "contrato", "orçamento", "cronograma"],
}
