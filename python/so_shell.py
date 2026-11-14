"""Shell mínimo: parser de linha de comando e execução de comandos simulados.

Suporta aspas simples/duplas, `$?`, listas com `;`, `&&` e `||`, pipelines com
`|` e redirecionamentos `<`, `>`, `>>`, `2>`, `2>>` e `2>&1`. A execução usa os
descritores de `so_pipes`: cada estágio é um "fork" da tabela do shell, ajustada
com dup2, e o shell fecha suas cópias das pontas dos pipes (senão não há EOF).

Comandos: echo, cat, grep (-v -c -i, regex), wc (-l -w -c), sort (-r -n), uniq (-c),
head/tail (-n N), ls, rm, tee, true, false.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from so_pipes import Sistema, TabelaFDs

_STATUS = "\x00STATUS\x00"
_OPERADORES = ("2>&1", "2>>", "2>", ">>", ">", "<", "&&", "||", "|", ";")


class ErroSintaxe(Exception):
    pass


@dataclass
class Redirecionamento:
    op: str  # "<", ">", ">>", "2>", "2>>", "2>&1"
    alvo: str = ""


@dataclass
class Comando:
    argv: list[str]
    redirs: list[Redirecionamento] = field(default_factory=list)


@dataclass
class Pipeline:
    comandos: list[Comando]


Token = tuple[str, str]  # ("palavra" | "op", texto)


def tokenizar(linha: str) -> list[Token]:
    tokens: list[Token] = []
    i, n = 0, len(linha)
    while i < n:
        c = linha[i]
        if c in " \t":
            i += 1
            continue
        op = next((o for o in _OPERADORES if linha.startswith(o, i)), None)
        if op is not None:
            tokens.append(("op", op))
            i += len(op)
            continue
        palavra = ""
        while i < n and linha[i] not in " \t":
            if linha[i] in "|<>;" or linha.startswith("&&", i):
                break
            c = linha[i]
            if c == "'":
                fim = linha.find("'", i + 1)
                if fim < 0:
                    raise ErroSintaxe("aspas simples sem fechamento")
                palavra += linha[i + 1 : fim]
                i = fim + 1
            elif c == '"':
                fim = linha.find('"', i + 1)
                if fim < 0:
                    raise ErroSintaxe("aspas duplas sem fechamento")
                palavra += linha[i + 1 : fim].replace("$?", _STATUS)
                i = fim + 1
            else:
                if linha.startswith("$?", i):
                    palavra += _STATUS
                    i += 2
                else:
                    palavra += c
                    i += 1
        tokens.append(("palavra", palavra))
    return tokens


def parse(linha: str) -> list[tuple[str, Pipeline]]:
    """Retorna [(conector_anterior, pipeline)]; o primeiro conector é ';'."""
    tokens = tokenizar(linha)
    resultado: list[tuple[str, Pipeline]] = []
    conector = ";"
    atual = Comando([])
    comandos: list[Comando] = []
    i = 0

    def fechar_comando() -> None:
        nonlocal atual
        if not atual.argv:
            raise ErroSintaxe("comando vazio")
        comandos.append(atual)
        atual = Comando([])

    while i < len(tokens):
        tipo, valor = tokens[i]
        if tipo == "palavra":
            atual.argv.append(valor)
        elif valor in ("<", ">", ">>", "2>", "2>>"):
            if i + 1 >= len(tokens) or tokens[i + 1][0] != "palavra":
                raise ErroSintaxe(f"falta arquivo depois de {valor}")
            atual.redirs.append(Redirecionamento(valor, tokens[i + 1][1]))
            i += 1
        elif valor == "2>&1":
            atual.redirs.append(Redirecionamento("2>&1"))
        elif valor == "|":
            fechar_comando()
        else:  # ; && ||
            fechar_comando()
            resultado.append((conector, Pipeline(comandos[:])))
            comandos.clear()
            conector = valor
        i += 1
    if atual.argv:
        fechar_comando()
        resultado.append((conector, Pipeline(comandos[:])))
    elif comandos or atual.redirs or conector != ";":
        raise ErroSintaxe("comando vazio no fim da linha")
    return resultado


# ---------- comandos simulados ----------
Builtin = Callable[[TabelaFDs, list[str]], int]


def _saida(t: TabelaFDs, texto: str) -> None:
    t.escrever(1, texto.encode())


def _erro(t: TabelaFDs, texto: str) -> None:
    t.escrever(2, (texto + "\n").encode())


def _entrada(t: TabelaFDs, arquivos: list[str], nome: str) -> Optional[str]:
    """Texto de stdin ou dos arquivos; None (com mensagem em stderr) se algum falhar."""
    if not arquivos:
        return t.ler_tudo(0).decode()
    partes = []
    for a in arquivos:
        if a not in t.sistema.arquivos:
            _erro(t, f"{nome}: {a}: arquivo inexistente")
            return None
        partes.append(bytes(t.sistema.arquivos[a]).decode())
    return "".join(partes)


def _linhas(texto: str) -> list[str]:
    return texto.splitlines()


def _opcao_n(args: list[str]) -> tuple[int, list[str]]:
    if len(args) >= 2 and args[0] == "-n" and args[1].lstrip("-").isdigit():
        return int(args[1]), args[2:]
    return 10, args


def cmd_echo(t: TabelaFDs, args: list[str]) -> int:
    nova_linha = True
    if args and args[0] == "-n":
        nova_linha, args = False, args[1:]
    _saida(t, " ".join(args) + ("\n" if nova_linha else ""))
    return 0


def cmd_cat(t: TabelaFDs, args: list[str]) -> int:
    texto = _entrada(t, args, "cat")
    if texto is None:
        return 1
    _saida(t, texto)
    return 0


def cmd_grep(t: TabelaFDs, args: list[str]) -> int:
    inverter = contar = ignorar = False
    while args and args[0] in ("-v", "-c", "-i"):
        flag, args = args[0], args[1:]
        inverter |= flag == "-v"
        contar |= flag == "-c"
        ignorar |= flag == "-i"
    if not args:
        _erro(t, "grep: faltou o padrão")
        return 2
    padrao = re.compile(args[0], re.IGNORECASE if ignorar else 0)
    texto = _entrada(t, args[1:], "grep")
    if texto is None:
        return 2
    achadas = [l for l in _linhas(texto) if bool(padrao.search(l)) != inverter]
    _saida(t, f"{len(achadas)}\n" if contar else "".join(l + "\n" for l in achadas))
    return 0 if achadas else 1


def cmd_wc(t: TabelaFDs, args: list[str]) -> int:
    flag = args[0] if args and args[0] in ("-l", "-w", "-c") else None
    texto = _entrada(t, args[1:] if flag else args, "wc")
    if texto is None:
        return 1
    contagens = {"-l": texto.count("\n"), "-w": len(texto.split()), "-c": len(texto.encode())}
    if flag:
        _saida(t, f"{contagens[flag]}\n")
    else:
        _saida(t, f"{contagens['-l']} {contagens['-w']} {contagens['-c']}\n")
    return 0


def cmd_sort(t: TabelaFDs, args: list[str]) -> int:
    reverso = numerico = False
    while args and args[0].startswith("-") and len(args[0]) > 1:
        reverso |= "r" in args[0]
        numerico |= "n" in args[0]
        args = args[1:]
    texto = _entrada(t, args, "sort")
    if texto is None:
        return 1

    def chave(linha: str):
        if numerico:
            m = re.match(r"\s*(-?\d+)", linha)
            return (int(m.group(1)) if m else 0, linha)
        return linha

    _saida(t, "".join(l + "\n" for l in sorted(_linhas(texto), key=chave, reverse=reverso)))
    return 0


def cmd_uniq(t: TabelaFDs, args: list[str]) -> int:
    contar = bool(args) and args[0] == "-c"
    texto = _entrada(t, args[1:] if contar else args, "uniq")
    if texto is None:
        return 1
    grupos: list[list] = []
    for l in _linhas(texto):
        if grupos and grupos[-1][0] == l:
            grupos[-1][1] += 1
        else:
            grupos.append([l, 1])
    _saida(t, "".join((f"{n:>7} {l}\n" if contar else f"{l}\n") for l, n in grupos))
    return 0


def cmd_head(t: TabelaFDs, args: list[str]) -> int:
    n, resto = _opcao_n(args)
    texto = _entrada(t, resto, "head")
    if texto is None:
        return 1
    _saida(t, "".join(l + "\n" for l in _linhas(texto)[:n]))
    return 0


def cmd_tail(t: TabelaFDs, args: list[str]) -> int:
    n, resto = _opcao_n(args)
    texto = _entrada(t, resto, "tail")
    if texto is None:
        return 1
    ls = _linhas(texto)
    _saida(t, "".join(l + "\n" for l in (ls[-n:] if n > 0 else [])))
    return 0


def cmd_ls(t: TabelaFDs, args: list[str]) -> int:
    _saida(t, "".join(n + "\n" for n in sorted(t.sistema.arquivos)))
    return 0


def cmd_rm(t: TabelaFDs, args: list[str]) -> int:
    status = 0
    for a in args:
        if a in t.sistema.arquivos:
            del t.sistema.arquivos[a]
        else:
            _erro(t, f"rm: {a}: arquivo inexistente")
            status = 1
    return status


def cmd_tee(t: TabelaFDs, args: list[str]) -> int:
    texto = t.ler_tudo(0).decode()
    for a in args:
        t.sistema.arquivos[a] = bytearray(texto.encode())
    _saida(t, texto)
    return 0


COMANDOS: dict[str, Builtin] = {
    "echo": cmd_echo,
    "cat": cmd_cat,
    "grep": cmd_grep,
    "wc": cmd_wc,
    "sort": cmd_sort,
    "uniq": cmd_uniq,
    "head": cmd_head,
    "tail": cmd_tail,
    "ls": cmd_ls,
    "rm": cmd_rm,
    "tee": cmd_tee,
    "true": lambda t, a: 0,
    "false": lambda t, a: 1,
}


class Shell:
    def __init__(self, sistema: Optional[Sistema] = None) -> None:
        self.sistema = sistema or Sistema()
        self.tabela = TabelaFDs(self.sistema)
        self.status = 0

    def _subst(self, argv: list[str]) -> list[str]:
        return [a.replace(_STATUS, str(self.status)) for a in argv]

    def _aplicar_redirs(self, filho: TabelaFDs, cmd: Comando) -> bool:
        for r in cmd.redirs:
            try:
                alvo = r.alvo.replace(_STATUS, str(self.status))
                if r.op == "2>&1":
                    filho.dup2(1, 2)
                    continue
                fd_alvo = {"<": 0, ">": 1, ">>": 1, "2>": 2, "2>>": 2}[r.op]
                modo = {"<": "r", ">": "w", ">>": "a", "2>": "w", "2>>": "a"}[r.op]
                fd = filho.abrir(alvo, modo)
                filho.dup2(fd, fd_alvo)
                filho.fechar(fd)
            except FileNotFoundError:
                filho.escrever(2, f"sh: {r.alvo}: arquivo inexistente\n".encode())
                return False
        return True

    def _estagio(self, cmd: Comando, entrada: Optional[int], saida: Optional[int]) -> int:
        filho = self.tabela.clonar()  # fork
        if entrada is not None:
            filho.dup2(entrada, 0)
        if saida is not None:
            filho.dup2(saida, 1)
        for fd in [fd for fd in filho.fds if fd > 2]:
            filho.fechar(fd)  # o filho só mantém 0, 1 e 2
        try:
            if not self._aplicar_redirs(filho, cmd):
                return 1
            argv = self._subst(cmd.argv)
            programa = COMANDOS.get(argv[0])
            if programa is None:
                filho.escrever(2, f"sh: {argv[0]}: comando não encontrado\n".encode())
                return 127
            return programa(filho, argv[1:])
        finally:
            filho.fechar_todos()

    def _pipeline(self, p: Pipeline) -> int:
        n = len(p.comandos)
        pipes = [self.tabela.criar_pipe(1 << 20) for _ in range(n - 1)]
        status = 0
        for i, cmd in enumerate(p.comandos):
            entrada = pipes[i - 1][0] if i > 0 else None
            saida = pipes[i][1] if i < n - 1 else None
            status = self._estagio(cmd, entrada, saida)
            if i > 0:
                self.tabela.fechar(pipes[i - 1][0])  # o pai fecha suas cópias
            if i < n - 1:
                self.tabela.fechar(pipes[i][1])
        return status

    def executar(self, linha: str) -> int:
        try:
            lista = parse(linha)
        except ErroSintaxe as e:
            self.tabela.escrever(2, f"sh: erro de sintaxe: {e}\n".encode())
            self.status = 2
            return 2
        for conector, pipeline in lista:
            if conector == "&&" and self.status != 0:
                continue
            if conector == "||" and self.status == 0:
                continue
            self.status = self._pipeline(pipeline)
        return self.status

    def saida(self) -> str:
        return bytes(self.sistema.stdout).decode()

    def erro(self) -> str:
        return bytes(self.sistema.stderr).decode()
