"""Pipes, descritores de arquivo e redirecionamento simulados.

Modelo Unix: cada tabela de descritores (fd -> descrição de arquivo aberto)
pertence a um processo; `dup`, `dup2` e `clonar` (fork) compartilham a mesma
descrição, com contagem de referências. Operações que bloqueariam um processo
real levantam `Bloquearia`, deixando a simulação determinística.

Semântica dos pipes: leitura retorna b"" (EOF) quando o buffer está vazio e não
há mais escritores; escrita sem leitores levanta `PipeQuebrado` (SIGPIPE).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union


class Bloquearia(Exception):
    """A operação bloquearia o processo (pipe vazio sem EOF ou pipe cheio)."""


class PipeQuebrado(Exception):
    pass


class ErroFD(Exception):
    pass


class Pipe:
    def __init__(self, capacidade: int = 64) -> None:
        if capacidade <= 0:
            raise ValueError("capacidade deve ser positiva")
        self.capacidade = capacidade
        self.buffer = bytearray()
        self.leitores = 0  # descrições abertas
        self.escritores = 0


@dataclass
class Descricao:
    tipo: str  # "pipe_r", "pipe_w", "arquivo", "stdin", "stdout", "stderr"
    pipe: Optional[Pipe] = None
    caminho: str = ""
    leitura: bool = False
    escrita: bool = False
    anexar: bool = False
    pos: int = 0
    refs: int = 1


@dataclass
class Sistema:
    """Estado compartilhado por todos os processos: arquivos e console."""

    arquivos: dict[str, bytearray] = field(default_factory=dict)
    stdin: bytearray = field(default_factory=bytearray)
    stdout: bytearray = field(default_factory=bytearray)
    stderr: bytearray = field(default_factory=bytearray)


class TabelaFDs:
    def __init__(self, sistema: Sistema, padrao: bool = True) -> None:
        self.sistema = sistema
        self.fds: dict[int, Descricao] = {}
        if padrao:
            self.fds[0] = Descricao("stdin", leitura=True)
            self.fds[1] = Descricao("stdout", escrita=True)
            self.fds[2] = Descricao("stderr", escrita=True)

    def _menor_livre(self) -> int:
        fd = 0
        while fd in self.fds:
            fd += 1
        return fd

    def _get(self, fd: int) -> Descricao:
        if fd not in self.fds:
            raise ErroFD(f"descritor inválido: {fd}")
        return self.fds[fd]

    # ---------- abertura ----------
    def abrir(self, caminho: str, modo: str) -> int:
        """modo: 'r' leitura, 'w' escrita (trunca), 'a' anexar."""
        arqs = self.sistema.arquivos
        if modo == "r":
            if caminho not in arqs:
                raise FileNotFoundError(caminho)
            d = Descricao("arquivo", caminho=caminho, leitura=True)
        elif modo in ("w", "a"):
            if modo == "w" or caminho not in arqs:
                arqs[caminho] = bytearray()
            d = Descricao("arquivo", caminho=caminho, escrita=True, anexar=modo == "a")
        else:
            raise ValueError(f"modo inválido: {modo}")
        fd = self._menor_livre()
        self.fds[fd] = d
        return fd

    def criar_pipe(self, capacidade: int = 64) -> tuple[int, int]:
        p = Pipe(capacidade)
        p.leitores = p.escritores = 1
        r = self._menor_livre()
        self.fds[r] = Descricao("pipe_r", pipe=p, leitura=True)
        w = self._menor_livre()
        self.fds[w] = Descricao("pipe_w", pipe=p, escrita=True)
        return r, w

    # ---------- duplicação ----------
    def dup(self, fd: int) -> int:
        d = self._get(fd)
        novo = self._menor_livre()
        self.fds[novo] = d
        d.refs += 1
        return novo

    def dup2(self, antigo: int, novo: int) -> int:
        d = self._get(antigo)
        if antigo == novo:
            return novo
        if novo in self.fds:
            self.fechar(novo)
        self.fds[novo] = d
        d.refs += 1
        return novo

    def clonar(self) -> "TabelaFDs":
        """Cópia da tabela como num fork: descrições compartilhadas."""
        filho = TabelaFDs(self.sistema, padrao=False)
        for fd, d in self.fds.items():
            filho.fds[fd] = d
            d.refs += 1
        return filho

    def fechar(self, fd: int) -> None:
        d = self._get(fd)
        del self.fds[fd]
        d.refs -= 1
        if d.refs == 0 and d.pipe is not None:
            if d.tipo == "pipe_r":
                d.pipe.leitores -= 1
            else:
                d.pipe.escritores -= 1

    def fechar_todos(self) -> None:
        for fd in list(self.fds):
            self.fechar(fd)

    # ---------- E/S ----------
    def ler(self, fd: int, n: int) -> bytes:
        d = self._get(fd)
        if not d.leitura:
            raise ErroFD(f"descritor {fd} não é de leitura")
        if d.tipo == "pipe_r":
            assert d.pipe is not None
            pipe = d.pipe
            if pipe.buffer:
                dados = bytes(pipe.buffer[:n])
                del pipe.buffer[:n]
                return dados
            if pipe.escritores == 0:
                return b""
            raise Bloquearia("pipe vazio")
        fonte: Union[bytearray, None]
        if d.tipo == "stdin":
            dados = bytes(self.sistema.stdin[:n])
            del self.sistema.stdin[:n]
            return dados
        fonte = self.sistema.arquivos[d.caminho]
        dados = bytes(fonte[d.pos : d.pos + n])
        d.pos += len(dados)
        return dados

    def escrever(self, fd: int, dados: bytes) -> int:
        d = self._get(fd)
        if not d.escrita:
            raise ErroFD(f"descritor {fd} não é de escrita")
        if d.tipo == "pipe_w":
            assert d.pipe is not None
            pipe = d.pipe
            if pipe.leitores == 0:
                raise PipeQuebrado("sem leitores")
            espaco = pipe.capacidade - len(pipe.buffer)
            if espaco == 0:
                raise Bloquearia("pipe cheio")
            pipe.buffer += dados[:espaco]
            return min(espaco, len(dados))
        if d.tipo == "stdout":
            self.sistema.stdout += dados
            return len(dados)
        if d.tipo == "stderr":
            self.sistema.stderr += dados
            return len(dados)
        alvo = self.sistema.arquivos[d.caminho]
        if d.anexar:
            d.pos = len(alvo)
        alvo[d.pos : d.pos + len(dados)] = dados
        d.pos += len(dados)
        return len(dados)

    def ler_tudo(self, fd: int) -> bytes:
        """Lê até EOF (propaga Bloquearia se o pipe ainda tem escritores)."""
        saida = b""
        while True:
            parte = self.ler(fd, 4096)
            if not parte:
                return saida
            saida += parte
