"""Formatador de mensagens de erro do compilador de Mini, com trecho e seta.

Exemplo::

    prog.mini:2:7: erro de sintaxe: esperado ';', encontrado 'var'
      2 | var y = 2
        |       ^

Erros sem posição (``linha == 0``, como os de execução) saem só com a linha
de cabeçalho. Tabulações são expandidas para 4 espaços e a seta acompanha.
"""
from __future__ import annotations

from comp_lexer import ErroLexico, ErroMini
from comp_parser import ErroSintaxe
from comp_semantica import ErroSemantico
from comp_simbolos import ErroRedeclaracao
from comp_tipos import ErroTipo
from comp_vm import ErroExecucao

TAB = 4
ROTULOS: list[tuple[type, str]] = [
    (ErroLexico, "erro léxico"),
    (ErroSintaxe, "erro de sintaxe"),
    (ErroRedeclaracao, "erro semântico"),
    (ErroSemantico, "erro semântico"),
    (ErroTipo, "erro de tipo"),
    (ErroExecucao, "erro de execução"),
]


def rotulo_do_erro(erro: ErroMini) -> str:
    for cls, nome in ROTULOS:
        if isinstance(erro, cls):
            return nome
    return "erro"


def formatar_erro(fonte: str, erro: ErroMini, arquivo: str = "<mini>") -> str:
    rotulo = rotulo_do_erro(erro)
    if erro.linha <= 0:
        return f"{arquivo}: {rotulo}: {erro.mensagem}"
    cabecalho = f"{arquivo}:{erro.linha}:{erro.coluna}: {rotulo}: {erro.mensagem}"
    linhas = fonte.split("\n")
    texto = linhas[erro.linha - 1].rstrip("\r") if erro.linha <= len(linhas) else ""
    antes = texto[:max(0, erro.coluna - 1)]
    exibido = texto.replace("\t", " " * TAB)
    recuo = len(antes.replace("\t", " " * TAB))
    # a seta não pode passar do fim do texto (exceto 1 caractere no fim da linha)
    largura = max(1, min(erro.tamanho, max(1, len(exibido) - recuo)))
    num = str(erro.linha)
    margem = " " * len(num)
    return (f"{cabecalho}\n"
            f"  {num} | {exibido}\n"
            f"  {margem} | {' ' * recuo}{'^' * largura}")


def formatar_erros(fonte: str, erros: list[ErroMini], arquivo: str = "<mini>") -> str:
    """Vários erros em ordem de posição, mais uma linha de resumo."""
    ordenados = sorted(erros, key=lambda e: (e.linha, e.coluna))
    blocos = [formatar_erro(fonte, e, arquivo) for e in ordenados]
    n = len(erros)
    blocos.append(f"{n} erro{'s' if n != 1 else ''}")
    return "\n".join(blocos)
