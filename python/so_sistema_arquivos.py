"""Sistema de arquivos em memória no estilo Unix.

- Disco: blocos de `tam_bloco` bytes controlados por um bitmap.
- Inode: tipo, tamanho, contagem de links, `N_DIRETOS` ponteiros diretos e um
  ponteiro indireto simples (o próprio bloco indireto consome um bloco do disco).
- Diretórios mapeiam nome -> número do inode; caminhos absolutos e relativos
  (com `.` e `..`) são resolvidos a partir do diretório de trabalho.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

N_DIRETOS = 2
PONTEIROS_POR_INDIRETO = 4


class ErroFS(Exception):
    pass


class NaoEncontrado(ErroFS):
    pass


class JaExiste(ErroFS):
    pass


class NaoEhDiretorio(ErroFS):
    pass


class EhDiretorio(ErroFS):
    pass


class DiretorioNaoVazio(ErroFS):
    pass


class SemEspaco(ErroFS):
    pass


class ArquivoGrande(ErroFS):
    pass


@dataclass
class Inode:
    tipo: str  # "arq" ou "dir"
    tamanho: int = 0
    nlinks: int = 1
    diretos: list[int] = field(default_factory=list)
    indireto: Optional[int] = None
    entradas: dict[str, int] = field(default_factory=dict)  # só para diretórios


class SistemaArquivos:
    def __init__(self, nblocos: int = 32, tam_bloco: int = 16) -> None:
        self.tam_bloco = tam_bloco
        self.blocos = [bytearray(tam_bloco) for _ in range(nblocos)]
        self.ocupado = [False] * nblocos
        self.ponteiros: dict[int, list[int]] = {}  # conteúdo dos blocos indiretos
        self.inodes: dict[int, Inode] = {0: Inode("dir", nlinks=2)}
        self._proximo = 1
        self.cwd = 0
        self.capacidade_maxima = (N_DIRETOS + PONTEIROS_POR_INDIRETO) * tam_bloco

    # ---------- caminhos ----------
    def _resolver(self, caminho: str) -> int:
        if not caminho:
            raise NaoEncontrado("caminho vazio")
        atual = 0 if caminho.startswith("/") else self.cwd
        pais = [0] if atual == 0 else self._cadeia(atual)
        for parte in caminho.split("/"):
            if parte in ("", "."):
                continue
            if parte == "..":
                if len(pais) > 1:
                    pais.pop()
                atual = pais[-1]
                continue
            ino = self.inodes[atual]
            if ino.tipo != "dir":
                raise NaoEhDiretorio(parte)
            if parte not in ino.entradas:
                raise NaoEncontrado(caminho)
            atual = ino.entradas[parte]
            pais.append(atual)
        return atual

    def _cadeia(self, inum: int) -> list[int]:
        """Cadeia de inodes da raiz até o diretório `inum`."""
        def busca(no: int, trilha: list[int]) -> Optional[list[int]]:
            if no == inum:
                return trilha
            for filho in self.inodes[no].entradas.values():
                if self.inodes[filho].tipo == "dir":
                    achou = busca(filho, trilha + [filho])
                    if achou:
                        return achou
            return None

        achou = busca(0, [0])
        assert achou is not None
        return achou

    def _pai_e_nome(self, caminho: str) -> tuple[int, str]:
        limpo = caminho.rstrip("/")
        if not limpo or limpo.split("/")[-1] in (".", ".."):
            raise ErroFS(f"nome inválido: {caminho!r}")
        if "/" in limpo:
            cabeca, nome = limpo.rsplit("/", 1)
            pai = self._resolver(cabeca or "/")
        else:
            nome, pai = limpo, self.cwd
        if self.inodes[pai].tipo != "dir":
            raise NaoEhDiretorio(caminho)
        return pai, nome

    def caminho_atual(self) -> str:
        if self.cwd == 0:
            return "/"
        trilha = self._cadeia(self.cwd)
        nomes = []
        for pai, filho in zip(trilha, trilha[1:]):
            nomes.append(next(n for n, i in self.inodes[pai].entradas.items() if i == filho))
        return "/" + "/".join(nomes)

    # ---------- blocos ----------
    def livres(self) -> int:
        return self.ocupado.count(False)

    def _alocar_bloco(self) -> int:
        for i, usado in enumerate(self.ocupado):
            if not usado:
                self.ocupado[i] = True
                self.blocos[i] = bytearray(self.tam_bloco)
                return i
        raise SemEspaco("disco cheio")

    def _blocos_do_inode(self, ino: Inode) -> list[int]:
        dados = list(ino.diretos)
        if ino.indireto is not None:
            dados += self.ponteiros[ino.indireto]
        return dados

    def _liberar_dados(self, ino: Inode) -> None:
        for b in self._blocos_do_inode(ino):
            self.ocupado[b] = False
        if ino.indireto is not None:
            self.ocupado[ino.indireto] = False
            del self.ponteiros[ino.indireto]
        ino.diretos, ino.indireto, ino.tamanho = [], None, 0

    @staticmethod
    def _blocos_necessarios(tamanho: int, tam_bloco: int) -> int:
        dados = -(-tamanho // tam_bloco)
        return dados + (1 if dados > N_DIRETOS else 0)

    # ---------- operações ----------
    def mkdir(self, caminho: str) -> int:
        pai, nome = self._pai_e_nome(caminho)
        if nome in self.inodes[pai].entradas:
            raise JaExiste(caminho)
        inum = self._novo_inode("dir")
        self.inodes[inum].nlinks = 2
        self.inodes[pai].entradas[nome] = inum
        return inum

    def _novo_inode(self, tipo: str) -> int:
        inum = self._proximo
        self._proximo += 1
        self.inodes[inum] = Inode(tipo)
        return inum

    def escrever(self, caminho: str, dados: bytes) -> int:
        """Cria ou sobrescreve um arquivo; devolve o número do inode."""
        if len(dados) > self.capacidade_maxima:
            raise ArquivoGrande(f"máximo de {self.capacidade_maxima} bytes")
        pai, nome = self._pai_e_nome(caminho)
        existente = self.inodes[pai].entradas.get(nome)
        if existente is not None and self.inodes[existente].tipo == "dir":
            raise EhDiretorio(caminho)
        reaproveitaveis = 0
        if existente is not None:
            ino = self.inodes[existente]
            reaproveitaveis = len(self._blocos_do_inode(ino)) + (ino.indireto is not None)
        if self._blocos_necessarios(len(dados), self.tam_bloco) > self.livres() + reaproveitaveis:
            raise SemEspaco("sem blocos livres suficientes")
        if existente is None:
            inum = self._novo_inode("arq")
            self.inodes[pai].entradas[nome] = inum
        else:
            inum = existente
            self._liberar_dados(self.inodes[inum])
        ino = self.inodes[inum]
        pedacos = [dados[i : i + self.tam_bloco] for i in range(0, len(dados), self.tam_bloco)]
        indiretos: list[int] = []
        for k, pedaco in enumerate(pedacos):
            if k == N_DIRETOS:
                ino.indireto = self._alocar_bloco()
            b = self._alocar_bloco()
            self.blocos[b][: len(pedaco)] = pedaco
            (ino.diretos if k < N_DIRETOS else indiretos).append(b)
        if ino.indireto is not None:
            self.ponteiros[ino.indireto] = indiretos
        ino.tamanho = len(dados)
        return inum

    def ler(self, caminho: str) -> bytes:
        ino = self.inodes[self._resolver(caminho)]
        if ino.tipo == "dir":
            raise EhDiretorio(caminho)
        bruto = b"".join(bytes(self.blocos[b]) for b in self._blocos_do_inode(ino))
        return bruto[: ino.tamanho]

    def listar(self, caminho: str = ".") -> list[str]:
        ino = self.inodes[self._resolver(caminho)]
        if ino.tipo != "dir":
            raise NaoEhDiretorio(caminho)
        return sorted(ino.entradas)

    def cd(self, caminho: str) -> None:
        inum = self._resolver(caminho)
        if self.inodes[inum].tipo != "dir":
            raise NaoEhDiretorio(caminho)
        self.cwd = inum

    def stat(self, caminho: str) -> dict[str, object]:
        inum = self._resolver(caminho)
        ino = self.inodes[inum]
        return {
            "inode": inum,
            "tipo": ino.tipo,
            "tamanho": ino.tamanho,
            "nlinks": ino.nlinks,
            "diretos": list(ino.diretos),
            "indireto": ino.indireto,
            "blocos": self._blocos_do_inode(ino),
        }

    def link(self, origem: str, destino: str) -> None:
        """Link físico (hard link) para um arquivo regular."""
        inum = self._resolver(origem)
        if self.inodes[inum].tipo == "dir":
            raise EhDiretorio(origem)
        pai, nome = self._pai_e_nome(destino)
        if nome in self.inodes[pai].entradas:
            raise JaExiste(destino)
        self.inodes[pai].entradas[nome] = inum
        self.inodes[inum].nlinks += 1

    def remover(self, caminho: str) -> None:
        """Remove arquivo (ou link) ou diretório vazio."""
        pai, nome = self._pai_e_nome(caminho)
        inum = self.inodes[pai].entradas.get(nome)
        if inum is None:
            raise NaoEncontrado(caminho)
        ino = self.inodes[inum]
        if ino.tipo == "dir":
            if ino.entradas:
                raise DiretorioNaoVazio(caminho)
            if inum == self.cwd:
                raise ErroFS("não é possível remover o diretório de trabalho")
            del self.inodes[inum]
        else:
            ino.nlinks -= 1
            if ino.nlinks == 0:
                self._liberar_dados(ino)
                del self.inodes[inum]
        del self.inodes[pai].entradas[nome]
