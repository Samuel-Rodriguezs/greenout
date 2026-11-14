"""Agenda de contatos com busca e validacao simples."""
import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Contato:
    nome: str
    telefone: str
    email: str = ""


class Agenda:
    def __init__(self) -> None:
        self._contatos: Dict[str, Contato] = {}

    @staticmethod
    def _chave(nome: str) -> str:
        return nome.strip().lower()

    def adicionar(self, nome: str, telefone: str, email: str = "") -> Contato:
        if not nome.strip():
            raise ValueError("nome vazio")
        digitos = re.sub(r"\D", "", telefone)
        if not 8 <= len(digitos) <= 13:
            raise ValueError("telefone invalido")
        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("email invalido")
        chave = self._chave(nome)
        if chave in self._contatos:
            raise ValueError("contato ja existe")
        contato = Contato(nome.strip(), digitos, email)
        self._contatos[chave] = contato
        return contato

    def obter(self, nome: str) -> Contato:
        try:
            return self._contatos[self._chave(nome)]
        except KeyError:
            raise KeyError(f"contato {nome!r} nao encontrado") from None

    def remover(self, nome: str) -> None:
        self.obter(nome)
        del self._contatos[self._chave(nome)]

    def buscar(self, trecho: str) -> List[Contato]:
        t = trecho.lower()
        return sorted(
            (c for c in self._contatos.values() if t in c.nome.lower()),
            key=lambda c: c.nome.lower(),
        )

    def __len__(self) -> int:
        return len(self._contatos)
