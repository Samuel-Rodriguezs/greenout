"""Versionamento semântico: parse, comparação e intervalos (^, ~, >=, <, x, ranges com hífen)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering


class ErroSemver(ValueError):
    """Versão ou intervalo inválido."""


_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


@total_ordering
@dataclass(frozen=True)
class Versao:
    maior: int
    menor: int
    patch: int
    pre: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def _chave(self) -> tuple:
        # sem pré-release é MAIOR que com pré-release
        pre = (1, ()) if not self.pre else (0, tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in self.pre))
        return (self.maior, self.menor, self.patch, pre)

    def __eq__(self, outro: object) -> bool:
        return isinstance(outro, Versao) and self._chave() == outro._chave()

    def __lt__(self, outro: "Versao") -> bool:
        return self._chave() < outro._chave()

    def __hash__(self) -> int:
        return hash(self._chave())

    def __str__(self) -> str:
        s = f"{self.maior}.{self.menor}.{self.patch}"
        if self.pre:
            s += "-" + ".".join(self.pre)
        if self.build:
            s += "+" + ".".join(self.build)
        return s

    def incrementar(self, parte: str) -> "Versao":
        if parte == "maior":
            return Versao(self.maior + 1, 0, 0)
        if parte == "menor":
            return Versao(self.maior, self.menor + 1, 0)
        if parte == "patch":
            return Versao(self.maior, self.menor, self.patch + 1)
        raise ErroSemver(f"parte desconhecida: {parte}")


def parse(texto: str) -> Versao:
    m = _RE.match(texto.strip().lstrip("v"))
    if not m:
        raise ErroSemver(f"versão inválida: {texto!r}")
    a, b, c, pre, build = m.groups()
    return Versao(int(a), int(b), int(c), tuple(pre.split(".")) if pre else (), tuple(build.split(".")) if build else ())


def comparar(a: str, b: str) -> int:
    va, vb = parse(a), parse(b)
    return (va > vb) - (va < vb)


def _parcial(t: str) -> tuple[int | None, int | None, int | None, str]:
    m = re.fullmatch(r"v?(\d+|[xX*])(?:\.(\d+|[xX*]))?(?:\.(\d+|[xX*]))?(?:-([0-9A-Za-z.-]+))?", t)
    if not m:
        raise ErroSemver(f"versão parcial inválida: {t!r}")
    nums = [None if g is None or g in "xX*" else int(g) for g in m.groups()[:3]]
    return nums[0], nums[1], nums[2], m.group(4) or ""


def _comparador(op: str, t: str) -> list[tuple[str, Versao]]:
    M, m, p, pre = _parcial(t)
    if M is None:
        return [(">=", Versao(0, 0, 0))] if op in ("", "=", ">=", "^", "~") else [("<", Versao(0, 0, 0))]
    mm, pp = m or 0, p or 0
    base = Versao(M, mm, pp, tuple(pre.split(".")) if pre else ())
    if op in ("", "=") and (m is None or p is None):
        if m is None:
            return [(">=", base), ("<", Versao(M + 1, 0, 0))]
        return [(">=", base), ("<", Versao(M, mm + 1, 0))]
    if op in ("", "="):
        return [("=", base)]
    if op == "^":
        if M > 0 or m is None:
            alto = Versao(M + 1, 0, 0)
        elif mm > 0 or p is None:
            alto = Versao(0, mm + 1, 0)
        else:
            alto = Versao(0, 0, pp + 1)
        return [(">=", base), ("<", alto)]
    if op == "~":
        alto = Versao(M, mm + 1, 0) if m is not None else Versao(M + 1, 0, 0)
        return [(">=", base), ("<", alto)]
    if op == ">" and (m is None or p is None):
        topo = Versao(M + 1, 0, 0) if m is None else Versao(M, mm + 1, 0)
        return [(">=", topo)]
    if op == "<=" and (m is None or p is None):
        topo = Versao(M + 1, 0, 0) if m is None else Versao(M, mm + 1, 0)
        return [("<", topo)]
    return [(op, base)]


def _teste(op: str, v: Versao, alvo: Versao) -> bool:
    return {"=": v == alvo, ">": v > alvo, ">=": v >= alvo, "<": v < alvo, "<=": v <= alvo}[op]


def satisfaz(versao: str, intervalo: str) -> bool:
    """Verifica se a versão satisfaz o intervalo (alternativas separadas por '||')."""
    v = parse(versao)
    for alt in intervalo.split("||"):
        alt = alt.strip()
        if not alt:
            alt = "*"
        alt = re.sub(r"^(\S+)\s+-\s+(\S+)$", r">=\1 <=\2", alt)
        alt = re.sub(r"(>=|<=|>|<|=|\^|~)\s+", r"\1", alt)
        comps: list[tuple[str, Versao]] = []
        for tok in alt.split():
            m = re.fullmatch(r"(>=|<=|>|<|=|\^|~)?(.+)", tok)
            if not m:
                raise ErroSemver(f"comparador inválido: {tok!r}")
            comps += _comparador(m.group(1) or "", m.group(2))
        if all(_teste(op, v, alvo) for op, alvo in comps) and _pre_permitido(v, comps):
            return True
    return False


def v_tuple(v: Versao) -> tuple[int, int, int]:
    return (v.maior, v.menor, v.patch)


def _pre_permitido(v: Versao, comps: list[tuple[str, Versao]]) -> bool:
    """Pré-releases só entram se algum comparador tiver pré-release na mesma tupla maior.menor.patch."""
    if not v.pre:
        return True
    return any(alvo.pre and v_tuple(alvo) == v_tuple(v) for _, alvo in comps)


def maior_satisfatoria(versoes: list[str], intervalo: str) -> str | None:
    ok = [parse(v) for v in versoes if satisfaz(v, intervalo)]
    return str(max(ok)) if ok else None
