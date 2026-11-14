"""Representação intermediária de três endereços (TAC) para Mini.

Cada instrução tem no máximo um operador e três endereços. Operandos são
nomes (``str``) ou constantes (``int``/``bool``). Convenções::

    nome        variável do programa (sombreadas ganham sufixo: x, x.1, x.2)
    %t1         temporário        L1: rótulo

Instruções: ``d = a``, ``d = a op b``, ``d = op a``, ``goto L``,
``ifFalse c goto L``, ``param a``, ``d = call f, n``, ``return [a]``,
``print a`` e rótulos. ``&&`` e ``||`` são convertidos em saltos (curto-circuito).
Inclui um interpretador de TAC usado para validar a tradução.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Num, Programa, Retorno, Se,
                      Unario, Var)
from comp_folding import aplicar_binario, aplicar_unario
from comp_vm import ErroExecucao, formatar_valor

Operando = Union[int, bool, str]


@dataclass(frozen=True)
class Copia:
    dest: str
    src: Operando


@dataclass(frozen=True)
class Bin:
    dest: str
    op: str
    a: Operando
    b: Operando


@dataclass(frozen=True)
class Un:
    dest: str
    op: str
    a: Operando


@dataclass(frozen=True)
class Rotulo:
    nome: str


@dataclass(frozen=True)
class Salto:
    alvo: str


@dataclass(frozen=True)
class SaltoSeNao:
    cond: Operando
    alvo: str


@dataclass(frozen=True)
class Param:
    valor: Operando


@dataclass(frozen=True)
class Chama:
    dest: str
    func: str
    n_args: int


@dataclass(frozen=True)
class Retorna:
    valor: Optional[Operando] = None


@dataclass(frozen=True)
class Imprime:
    valor: Operando


Instrucao = Union[Copia, Bin, Un, Rotulo, Salto, SaltoSeNao, Param, Chama, Retorna, Imprime]


@dataclass
class FuncaoTAC:
    nome: str
    params: list[str]
    codigo: list[Instrucao] = field(default_factory=list)


@dataclass
class ProgramaTAC:
    funcoes: list[FuncaoTAC]
    principal: FuncaoTAC


def eh_variavel(o: object) -> bool:
    """True se o operando é um nome (e não uma constante)."""
    return isinstance(o, str)


def usados(i: Instrucao) -> list[str]:
    """Nomes lidos pela instrução."""
    if isinstance(i, Copia):
        ops: list[object] = [i.src]
    elif isinstance(i, Bin):
        ops = [i.a, i.b]
    elif isinstance(i, Un):
        ops = [i.a]
    elif isinstance(i, SaltoSeNao):
        ops = [i.cond]
    elif isinstance(i, Param):
        ops = [i.valor]
    elif isinstance(i, Retorna):
        ops = [i.valor]
    elif isinstance(i, Imprime):
        ops = [i.valor]
    else:
        ops = []
    return [o for o in ops if isinstance(o, str)]


def definido(i: Instrucao) -> Optional[str]:
    """Nome escrito pela instrução, se houver."""
    if isinstance(i, (Copia, Bin, Un, Chama)):
        return i.dest
    return None


def formatar_instrucao(i: Instrucao) -> str:
    def f(o: object) -> str:
        return str(o).lower() if isinstance(o, bool) else str(o)

    if isinstance(i, Copia):
        return f"{i.dest} = {f(i.src)}"
    if isinstance(i, Bin):
        return f"{i.dest} = {f(i.a)} {i.op} {f(i.b)}"
    if isinstance(i, Un):
        return f"{i.dest} = {i.op}{f(i.a)}"
    if isinstance(i, Rotulo):
        return f"{i.nome}:"
    if isinstance(i, Salto):
        return f"goto {i.alvo}"
    if isinstance(i, SaltoSeNao):
        return f"ifFalse {f(i.cond)} goto {i.alvo}"
    if isinstance(i, Param):
        return f"param {f(i.valor)}"
    if isinstance(i, Chama):
        return f"{i.dest} = call {i.func}, {i.n_args}"
    if isinstance(i, Retorna):
        return "return" if i.valor is None else f"return {f(i.valor)}"
    return f"print {f(i.valor)}"


def formatar_tac(p: ProgramaTAC) -> str:
    linhas: list[str] = []
    for fn in p.funcoes + [p.principal]:
        linhas.append(f"func {fn.nome}({', '.join(fn.params)}):")
        for i in fn.codigo:
            ind = "" if isinstance(i, Rotulo) else "    "
            linhas.append(ind + formatar_instrucao(i))
    return "\n".join(linhas)


class _GeradorTAC:
    def __init__(self) -> None:
        self.codigo: list[Instrucao] = []
        self.escopos: list[dict[str, str]] = [{}]
        self.usos_nome: dict[str, int] = {}
        self.n_temp = 0
        self.n_rotulo = 0

    def temp(self) -> str:
        self.n_temp += 1
        return f"%t{self.n_temp}"

    def rotulo(self) -> str:
        self.n_rotulo += 1
        return f"L{self.n_rotulo}"

    def declarar(self, nome: str) -> str:
        n = self.usos_nome.get(nome, 0)
        self.usos_nome[nome] = n + 1
        unico = nome if n == 0 else f"{nome}.{n}"
        self.escopos[-1][nome] = unico
        return unico

    def resolver(self, nome: str) -> str:
        for esc in reversed(self.escopos):
            if nome in esc:
                return esc[nome]
        raise KeyError(nome)

    def emitir(self, i: Instrucao) -> None:
        self.codigo.append(i)

    # --- expressões -------------------------------------------------------
    def expr(self, e: No) -> Operando:
        if isinstance(e, (Num, Bool)):
            return e.valor
        if isinstance(e, Nome):
            return self.resolver(e.nome)
        if isinstance(e, Unario):
            a = self.expr(e.operando)
            t = self.temp()
            self.emitir(Un(t, e.op, a))
            return t
        if isinstance(e, Binario):
            if e.op in ("&&", "||"):
                return self.logico(e)
            a = self.expr(e.esq)
            b = self.expr(e.dir)
            t = self.temp()
            self.emitir(Bin(t, e.op, a, b))
            return t
        if isinstance(e, Chamada):
            args = [self.expr(a) for a in e.args]
            for a in args:
                self.emitir(Param(a))
            t = self.temp()
            self.emitir(Chama(t, e.nome, len(args)))
            return t
        raise TypeError(f"expressão inválida: {type(e).__name__}")

    def logico(self, e: Binario) -> Operando:
        r = self.temp()
        fim = self.rotulo()
        self.emitir(Copia(r, self.expr(e.esq)))
        if e.op == "&&":
            self.emitir(SaltoSeNao(r, fim))
        else:
            n = self.temp()
            self.emitir(Un(n, "!", r))
            self.emitir(SaltoSeNao(n, fim))
        self.emitir(Copia(r, self.expr(e.dir)))
        self.emitir(Rotulo(fim))
        return r

    # --- comandos ---------------------------------------------------------
    def bloco(self, b: Bloco) -> None:
        self.escopos.append({})
        for s in b.stmts:
            self.stmt(s)
        self.escopos.pop()

    def stmt(self, s: No) -> None:
        if isinstance(s, Var):
            valor = self.expr(s.init)
            self.emitir(Copia(self.declarar(s.nome), valor))
        elif isinstance(s, Atrib):
            self.emitir(Copia(self.resolver(s.nome), self.expr(s.valor)))
        elif isinstance(s, Imprimir):
            self.emitir(Imprime(self.expr(s.valor)))
        elif isinstance(s, ExprStmt):
            self.expr(s.expr)
        elif isinstance(s, Bloco):
            self.bloco(s)
        elif isinstance(s, Retorno):
            self.emitir(Retorna(None if s.valor is None else self.expr(s.valor)))
        elif isinstance(s, Se):
            c = self.expr(s.cond)
            fim = self.rotulo()
            if s.senao is None:
                self.emitir(SaltoSeNao(c, fim))
                self.bloco(s.entao)
            else:
                senao = self.rotulo()
                self.emitir(SaltoSeNao(c, senao))
                self.bloco(s.entao)
                self.emitir(Salto(fim))
                self.emitir(Rotulo(senao))
                self.bloco(s.senao)
            self.emitir(Rotulo(fim))
        elif isinstance(s, Enquanto):
            topo, fim = self.rotulo(), self.rotulo()
            self.emitir(Rotulo(topo))
            self.emitir(SaltoSeNao(self.expr(s.cond), fim))
            self.bloco(s.corpo)
            self.emitir(Salto(topo))
            self.emitir(Rotulo(fim))
        else:
            raise TypeError(f"comando inválido: {type(s).__name__}")


def gerar_tac(programa: Programa) -> ProgramaTAC:
    funcoes: list[FuncaoTAC] = []
    for f in programa.funcoes():
        g = _GeradorTAC()
        params = [g.declarar(p.nome) for p in f.params]
        g.escopos.append({})
        for s in f.corpo.stmts:
            g.stmt(s)
        g.emitir(Retorna(0))
        funcoes.append(FuncaoTAC(f.nome, params, g.codigo))
    g = _GeradorTAC()
    for item in programa.itens:
        if not isinstance(item, Funcao):
            g.stmt(item)
    g.emitir(Retorna(None))
    return ProgramaTAC(funcoes, FuncaoTAC("main", [], g.codigo))


def executar_tac(programa: ProgramaTAC, max_passos: int = 5_000_000,
                 max_profundidade: int = 200) -> list[str]:
    """Interpreta o TAC e devolve as linhas impressas."""
    funcoes = {f.nome: f for f in programa.funcoes}
    saida: list[str] = []
    passos = 0
    rotulos = {id(f): {i.nome: k for k, i in enumerate(f.codigo) if isinstance(i, Rotulo)}
               for f in programa.funcoes + [programa.principal]}

    def rodar(f: FuncaoTAC, args: list[object], prof: int) -> object:
        nonlocal passos
        if prof > max_profundidade:
            raise ErroExecucao("estouro da pilha de chamadas")
        env: dict[str, object] = dict(zip(f.params, args))
        pendentes: list[object] = []

        def val(o: Operando) -> object:
            return env[o] if isinstance(o, str) else o

        pc = 0
        while pc < len(f.codigo):
            passos += 1
            if passos > max_passos:
                raise ErroExecucao("limite de passos excedido")
            i = f.codigo[pc]
            pc += 1
            try:
                if isinstance(i, Copia):
                    env[i.dest] = val(i.src)
                elif isinstance(i, Bin):
                    env[i.dest] = aplicar_binario(i.op, val(i.a), val(i.b))
                elif isinstance(i, Un):
                    env[i.dest] = aplicar_unario(i.op, val(i.a))
            except ZeroDivisionError:
                raise ErroExecucao("divisão por zero") from None
            if isinstance(i, Salto):
                pc = rotulos[id(f)][i.alvo]
            elif isinstance(i, SaltoSeNao):
                if not val(i.cond):
                    pc = rotulos[id(f)][i.alvo]
            elif isinstance(i, Param):
                pendentes.append(val(i.valor))
            elif isinstance(i, Chama):
                args_ = pendentes[len(pendentes) - i.n_args:]
                del pendentes[len(pendentes) - i.n_args:]
                env[i.dest] = rodar(funcoes[i.func], args_, prof + 1)
            elif isinstance(i, Retorna):
                return 0 if i.valor is None else val(i.valor)
            elif isinstance(i, Imprime):
                saida.append(formatar_valor(val(i.valor)))
        return 0

    rodar(programa.principal, [], 0)
    return saida
