"""Diff unificado: gerar (via LCS) e aplicar patches, com verificação de contexto."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


class ErroPatch(ValueError):
    """Patch malformado ou que não se aplica ao texto."""


@dataclass
class Hunk:
    inicio_a: int  # 1-based
    tam_a: int
    inicio_b: int
    tam_b: int
    linhas: list[str] = field(default_factory=list)  # com prefixo ' ', '+' ou '-'


def _operacoes(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """Script de edição mínimo via tabela LCS: lista de (' '|'-'|'+', linha)."""
    n, m = len(a), len(b)
    # remove prefixo/sufixo comum para reduzir a tabela
    ini = 0
    while ini < n and ini < m and a[ini] == b[ini]:
        ini += 1
    fim = 0
    while fim < n - ini and fim < m - ini and a[n - 1 - fim] == b[m - 1 - fim]:
        fim += 1
    ma, mb = a[ini:n - fim], b[ini:m - fim]
    p, q = len(ma), len(mb)
    t = [[0] * (q + 1) for _ in range(p + 1)]
    for i in range(p - 1, -1, -1):
        for j in range(q - 1, -1, -1):
            t[i][j] = t[i + 1][j + 1] + 1 if ma[i] == mb[j] else max(t[i + 1][j], t[i][j + 1])
    ops = [(" ", x) for x in a[:ini]]
    i = j = 0
    while i < p and j < q:
        if ma[i] == mb[j]:
            ops.append((" ", ma[i]))
            i += 1
            j += 1
        elif t[i + 1][j] >= t[i][j + 1]:
            ops.append(("-", ma[i]))
            i += 1
        else:
            ops.append(("+", mb[j]))
            j += 1
    ops += [("-", x) for x in ma[i:]] + [("+", x) for x in mb[j:]]
    ops += [(" ", x) for x in a[n - fim:]]
    return ops


def _dividir(texto: str) -> list[str]:
    return texto.split("\n")[:-1] if texto.endswith("\n") else texto.split("\n") if texto else []


def gerar(antigo: str, novo: str, nome_a: str = "a", nome_b: str = "b", contexto: int = 3) -> str:
    """Gera diff unificado. Retorna '' se os textos forem iguais.

    Textos devem terminar em '\\n' (o marcador 'sem quebra de linha' não é suportado).
    """
    for t in (antigo, novo):
        if t and not t.endswith("\n"):
            raise ErroPatch("texto sem quebra de linha final não é suportado")
    a, b = _dividir(antigo), _dividir(novo)
    ops = _operacoes(a, b)
    mudancas = [i for i, (o, _) in enumerate(ops) if o != " "]
    if not mudancas:
        return ""
    # agrupa mudanças cujo contexto se sobrepõe
    grupos: list[tuple[int, int]] = []
    ini = fim = mudancas[0]
    for i in mudancas[1:]:
        if i - fim <= 2 * contexto:
            fim = i
        else:
            grupos.append((ini, fim))
            ini = fim = i
    grupos.append((ini, fim))
    saida = [f"--- {nome_a}", f"+++ {nome_b}"]
    for ini, fim in grupos:
        de, ate = max(0, ini - contexto), min(len(ops), fim + contexto + 1)
        antes_a = sum(1 for o, _ in ops[:de] if o != "+")
        antes_b = sum(1 for o, _ in ops[:de] if o != "-")
        fatia = ops[de:ate]
        tam_a = sum(1 for o, _ in fatia if o != "+")
        tam_b = sum(1 for o, _ in fatia if o != "-")
        ia = antes_a + 1 if tam_a else antes_a
        ib = antes_b + 1 if tam_b else antes_b
        saida.append(f"@@ -{ia},{tam_a} +{ib},{tam_b} @@")
        saida += [o + l for o, l in fatia]
    return "\n".join(saida) + "\n"


def parse_patch(patch: str) -> list[Hunk]:
    linhas = patch.split("\n")
    if linhas and linhas[-1] == "":
        linhas.pop()
    i = 0
    if len(linhas) >= 2 and linhas[0].startswith("--- ") and linhas[1].startswith("+++ "):
        i = 2
    hunks: list[Hunk] = []
    while i < len(linhas):
        m = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*", linhas[i])
        if not m:
            raise ErroPatch(f"cabeçalho de hunk esperado na linha {i + 1}: {linhas[i]!r}")
        ia, ta, ib, tb = m.groups()
        h = Hunk(int(ia), int(ta) if ta is not None else 1, int(ib), int(tb) if tb is not None else 1)
        i += 1
        cont_a = cont_b = 0
        while i < len(linhas) and (cont_a < h.tam_a or cont_b < h.tam_b):
            l = linhas[i]
            if not l or l[0] not in " +-":
                raise ErroPatch(f"linha inválida dentro do hunk (linha {i + 1}): {l!r}")
            if l[0] != "+":
                cont_a += 1
            if l[0] != "-":
                cont_b += 1
            h.linhas.append(l)
            i += 1
        if cont_a != h.tam_a or cont_b != h.tam_b:
            raise ErroPatch("hunk truncado: contagem de linhas não confere com o cabeçalho")
        hunks.append(h)
    if not hunks:
        raise ErroPatch("patch sem hunks")
    return hunks


def aplicar(original: str, patch: str, reverso: bool = False) -> str:
    """Aplica o patch ao texto, verificando contexto e linhas removidas. Com reverso=True, desfaz."""
    if original and not original.endswith("\n"):
        raise ErroPatch("texto sem quebra de linha final não é suportado")
    linhas = _dividir(original)
    saida: list[str] = []
    pos = 0  # índice 0-based em `linhas`
    for h in parse_patch(patch):
        inicio = (h.inicio_b if reverso else h.inicio_a)
        tam = h.tam_b if reverso else h.tam_a
        alvo = inicio - 1 if tam else inicio
        if alvo < pos or alvo > len(linhas):
            raise ErroPatch(f"hunk fora de ordem ou fora do arquivo (@@ {h.inicio_a})")
        saida += linhas[pos:alvo]
        pos = alvo
        for l in h.linhas:
            op, txt = l[0], l[1:]
            if reverso:
                op = {"+": "-", "-": "+", " ": " "}[op]
            if op in " -":
                if pos >= len(linhas) or linhas[pos] != txt:
                    achado = linhas[pos] if pos < len(linhas) else "<fim do arquivo>"
                    raise ErroPatch(f"conflito na linha {pos + 1}: esperado {txt!r}, encontrado {achado!r}")
                pos += 1
                if op == " ":
                    saida.append(txt)
            else:
                saida.append(txt)
    saida += linhas[pos:]
    return "".join(l + "\n" for l in saida)
