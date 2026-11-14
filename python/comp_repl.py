"""REPL de Mini testável: uma função recebe linhas e devolve o texto de saída.

* entradas com ``{``, ``(`` ou comentário de bloco abertos pedem continuação
  (``aguardando_continuacao``);
* uma expressão sem ``;`` final é impressa (``1 + 2`` mostra ``3``);
* ``var`` de nível superior e ``func`` persistem entre entradas;
* erros saem formatados com trecho e seta (comp_erros) e não alteram o estado;
* comandos: ``:ajuda``, ``:vars``, ``:funcoes``, ``:ast <código>``,
  ``:tac <código>``, ``:limpar`` e ``:sair``.

O estado é reproduzido a cada entrada: as variáveis salvas viram ``var``
literais no início do programa e as funções são reaproveitadas da AST.
"""
from __future__ import annotations

from typing import Iterable

from comp_ast import (Bool, Chamada, ExprStmt, Funcao, Imprimir, No, Num, Programa,
                      Var)
from comp_erros import formatar_erro, formatar_erros
from comp_gerador import gerar
from comp_lexer import ErroLexico, ErroMini, TipoToken, tokenizar
from comp_parser import parse, parse_expressao
from comp_printer import dump
from comp_semantica import analisar
from comp_tac import formatar_tac, gerar_tac
from comp_tipos import verificar
from comp_vm import executar

AJUDA = """\
Comandos:
  :vars            lista as variáveis
  :funcoes         lista as funções
  :ast <código>    mostra a AST
  :tac <código>    mostra o código de três endereços
  :limpar          esquece variáveis e funções
  :sair            encerra
Expressões sem ';' têm o valor impresso; 'var' e 'func' persistem."""

PROMPT = "mini> "
PROMPT_CONTINUACAO = "...> "


class Repl:
    def __init__(self, arquivo: str = "<repl>") -> None:
        self.arquivo = arquivo
        self.funcoes: list[Funcao] = []
        self.variaveis: dict[str, int | bool] = {}
        self.buffer: list[str] = []
        self.encerrado = False

    @property
    def aguardando_continuacao(self) -> bool:
        return bool(self.buffer)

    # --- API ---------------------------------------------------------------
    def processar(self, linha: str) -> str:
        """Consome uma linha; devolve o texto a mostrar ('' se nada)."""
        if not self.buffer and linha.strip().startswith(":"):
            return self._comando(linha.strip())
        self.buffer.append(linha)
        texto = "\n".join(self.buffer)
        if not texto.strip():
            self.buffer.clear()
            return ""
        try:
            if self._incompleto(texto):
                return ""
        except ErroLexico as e:
            self.buffer.clear()
            return formatar_erro(texto, e, self.arquivo)
        self.buffer.clear()
        return self._avaliar(texto)

    def sessao(self, linhas: Iterable[str]) -> str:
        """Transcrição de uma sessão completa, com prompts e ecos das entradas."""
        saida: list[str] = []
        for linha in linhas:
            if self.encerrado:
                break
            prompt = PROMPT_CONTINUACAO if self.aguardando_continuacao else PROMPT
            saida.append(prompt + linha)
            resposta = self.processar(linha)
            if resposta:
                saida.append(resposta)
        return "\n".join(saida)

    # --- internos -----------------------------------------------------------
    @staticmethod
    def _incompleto(texto: str) -> bool:
        try:
            tokens = tokenizar(texto)
        except ErroLexico as e:
            if "não terminado" in e.mensagem:
                return True
            raise
        saldo = 0
        for t in tokens:
            if t.tipo is TipoToken.OP:
                if t.lexema in "({":
                    saldo += 1
                elif t.lexema in ")}":
                    saldo -= 1
        return saldo > 0

    def _comando(self, linha: str) -> str:
        nome, _, resto = linha.partition(" ")
        if nome == ":sair":
            self.encerrado = True
            return "tchau"
        if nome == ":ajuda":
            return AJUDA
        if nome == ":limpar":
            self.funcoes.clear()
            self.variaveis.clear()
            return "estado limpo"
        if nome == ":vars":
            if not self.variaveis:
                return "(nenhuma variável)"
            return "\n".join(f"{n}: {self._tipo(v)} = {self._texto(v)}"
                             for n, v in self.variaveis.items())
        if nome == ":funcoes":
            if not self.funcoes:
                return "(nenhuma função)"
            return "\n".join(
                f"{f.nome}({', '.join(f'{p.nome}: {p.tipo}' for p in f.params)}) -> {f.ret}"
                for f in self.funcoes)
        if nome in (":ast", ":tac"):
            try:
                programa = parse(resto)
            except ErroMini as e:
                return formatar_erro(resto, e, self.arquivo)
            return dump(programa) if nome == ":ast" else formatar_tac(gerar_tac(programa))
        return f"comando desconhecido: {nome} (use :ajuda)"

    @staticmethod
    def _tipo(v: int | bool) -> str:
        return "bool" if isinstance(v, bool) else "int"

    @staticmethod
    def _texto(v: int | bool) -> str:
        return ("true" if v else "false") if isinstance(v, bool) else str(v)

    def _novos_itens(self, texto: str) -> list[No]:
        """Interpreta a entrada: expressão avulsa vira print (ou chamada void)."""
        if not texto.rstrip().endswith((";", "}")):
            try:
                expr = parse_expressao(texto)
            except ErroMini:
                expr = None
            if expr is not None:
                void = isinstance(expr, Chamada) and any(
                    f.nome == expr.nome and f.ret == "void" for f in self.funcoes)
                return [ExprStmt(expr, pos=expr.pos) if void
                        else Imprimir(expr, pos=expr.pos)]
        return parse(texto).itens

    def _prelude(self) -> list[No]:
        itens: list[No] = list(self.funcoes)
        for nome, v in self.variaveis.items():
            lit = Bool(v) if isinstance(v, bool) else Num(v)
            itens.append(Var(nome, lit, self._tipo(v)))
        return itens

    def _avaliar(self, texto: str) -> str:
        try:
            novos = self._novos_itens(texto)
        except ErroMini as e:
            return formatar_erro(texto, e, self.arquivo)
        programa = Programa(self._prelude() + novos)
        erros: list[ErroMini] = list(analisar(programa).erros)
        if not erros:
            erros.extend(verificar(programa))
        if erros:
            return formatar_erros(texto, erros, self.arquivo)
        compilado = gerar(programa)
        try:
            resultado = executar(compilado)
        except ErroMini as e:
            return formatar_erro(texto, e, self.arquivo)
        self.funcoes.extend(i for i in novos if isinstance(i, Funcao))
        self.variaveis = {n: resultado.locais[s]
                          for n, s in compilado.nomes_principal.items()}
        return "\n".join(resultado.saida)
