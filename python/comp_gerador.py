"""Gerador de código: AST de Mini (já validada) para a VM de pilha de comp_vm.

* cada ``var``/parâmetro recebe um slot próprio de local (sem reuso);
* ``&&`` e ``||`` usam ``DUP``/``JZ`` para curto-circuito;
* todo comando de expressão descarta o valor com ``POP``;
* funções terminam com ``PUSH 0; RET`` implícito e o código de nível
  superior vira a função principal, terminada por ``HALT``.
"""
from __future__ import annotations

from comp_ast import (Atrib, Binario, Bloco, Bool, Chamada, Enquanto, ExprStmt,
                      Funcao, Imprimir, No, Nome, Num, Programa, Retorno, Se,
                      Unario, Var)
from comp_vm import FuncaoVM, Instr, Op, ProgramaVM, OP_BINARIO, OP_UNARIO

BINARIOS = {v: k for k, v in OP_BINARIO.items()}
UNARIOS = {v: k for k, v in OP_UNARIO.items()}


class _GeradorFuncao:
    def __init__(self, indices: dict[str, int]) -> None:
        self.indices = indices
        self.codigo: list[Instr] = []
        self.escopos: list[dict[str, int]] = [{}]
        self.n_locais = 0

    def emitir(self, op: Op, arg: object = None) -> int:
        self.codigo.append(Instr(op, arg))
        return len(self.codigo) - 1

    def remendar(self, posicao: int, destino: int) -> None:
        self.codigo[posicao] = Instr(self.codigo[posicao].op, destino)

    def novo_slot(self, nome: str) -> int:
        slot = self.n_locais
        self.n_locais += 1
        self.escopos[-1][nome] = slot
        return slot

    def slot(self, nome: str) -> int:
        for esc in reversed(self.escopos):
            if nome in esc:
                return esc[nome]
        raise KeyError(f"variável não resolvida: {nome}")

    # --- expressões -------------------------------------------------------
    def expr(self, e: No) -> None:
        if isinstance(e, (Num, Bool)):
            self.emitir(Op.PUSH, e.valor)
        elif isinstance(e, Nome):
            self.emitir(Op.LOAD, self.slot(e.nome))
        elif isinstance(e, Unario):
            self.expr(e.operando)
            self.emitir(UNARIOS[e.op])
        elif isinstance(e, Binario):
            if e.op in ("&&", "||"):
                self.logico(e)
            else:
                self.expr(e.esq)
                self.expr(e.dir)
                self.emitir(BINARIOS[e.op])
        elif isinstance(e, Chamada):
            for a in e.args:
                self.expr(a)
            self.emitir(Op.CALL, self.indices[e.nome])
        else:
            raise TypeError(f"expressão inválida: {type(e).__name__}")

    def logico(self, e: Binario) -> None:
        self.expr(e.esq)
        self.emitir(Op.DUP)
        if e.op == "||":
            self.emitir(Op.NOT)  # salta (mantendo o valor) quando o lado esquerdo é true
        salto = self.emitir(Op.JZ, None)
        self.emitir(Op.POP)
        self.expr(e.dir)
        self.remendar(salto, len(self.codigo))

    # --- comandos ---------------------------------------------------------
    def bloco(self, b: Bloco) -> None:
        self.escopos.append({})
        for s in b.stmts:
            self.stmt(s)
        self.escopos.pop()

    def stmt(self, s: No) -> None:
        if isinstance(s, Var):
            self.expr(s.init)  # avalia antes de declarar (var x = x vê o x externo)
            self.emitir(Op.STORE, self.novo_slot(s.nome))
        elif isinstance(s, Atrib):
            self.expr(s.valor)
            self.emitir(Op.STORE, self.slot(s.nome))
        elif isinstance(s, Imprimir):
            self.expr(s.valor)
            self.emitir(Op.PRINT)
        elif isinstance(s, ExprStmt):
            self.expr(s.expr)
            self.emitir(Op.POP)
        elif isinstance(s, Bloco):
            self.bloco(s)
        elif isinstance(s, Se):
            self.expr(s.cond)
            salto_senao = self.emitir(Op.JZ, None)
            self.bloco(s.entao)
            if s.senao is None:
                self.remendar(salto_senao, len(self.codigo))
            else:
                salto_fim = self.emitir(Op.JMP, None)
                self.remendar(salto_senao, len(self.codigo))
                self.bloco(s.senao)
                self.remendar(salto_fim, len(self.codigo))
        elif isinstance(s, Enquanto):
            topo = len(self.codigo)
            self.expr(s.cond)
            salto_fim = self.emitir(Op.JZ, None)
            self.bloco(s.corpo)
            self.emitir(Op.JMP, topo)
            self.remendar(salto_fim, len(self.codigo))
        elif isinstance(s, Retorno):
            if s.valor is None:
                self.emitir(Op.PUSH, 0)
            else:
                self.expr(s.valor)
            self.emitir(Op.RET)
        else:
            raise TypeError(f"comando inválido: {type(s).__name__}")


def gerar(programa: Programa) -> ProgramaVM:
    funcoes = programa.funcoes()
    indices = {f.nome: i for i, f in enumerate(funcoes)}
    compiladas: list[FuncaoVM] = []
    for f in funcoes:
        g = _GeradorFuncao(indices)
        for p in f.params:
            g.novo_slot(p.nome)
        g.escopos.append({})  # corpo: escopo interno ao dos parâmetros
        for s in f.corpo.stmts:
            g.stmt(s)
        g.emitir(Op.PUSH, 0)
        g.emitir(Op.RET)
        compiladas.append(FuncaoVM(f.nome, len(f.params), g.n_locais, g.codigo))
    g = _GeradorFuncao(indices)
    for item in programa.itens:
        if not isinstance(item, Funcao):
            g.stmt(item)
    g.emitir(Op.HALT)
    principal = FuncaoVM("main", 0, g.n_locais, g.codigo)
    return ProgramaVM(compiladas, principal, dict(g.escopos[0]))
