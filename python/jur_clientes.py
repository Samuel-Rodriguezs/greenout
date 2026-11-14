"""Cadastro de clientes do escritório (pessoa física e jurídica) com validação de documentos."""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from dt_cnpj import formatar_cnpj, validar_cnpj
from util_cpf import formatar_cpf, validar_cpf

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


class TipoPessoa(Enum):
    PF = "PF"
    PJ = "PJ"


@dataclass(frozen=True)
class Cliente:
    id: int
    tipo: TipoPessoa
    nome: str
    documento: str  # CPF ou CNPJ formatado
    email: str = ""
    telefone: str = ""


def _digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def criar_cliente(id: int, nome: str, documento: str, email: str = "", telefone: str = "") -> Cliente:
    """Detecta PF/PJ pelo documento e valida nome, documento, e-mail e telefone."""
    nome = " ".join(nome.split())
    if len(nome) < 3:
        raise ValueError("nome deve ter ao menos 3 caracteres")
    if email and not _EMAIL.match(email):
        raise ValueError("e-mail inválido")
    tel = _digitos(telefone)
    if telefone and len(tel) not in (10, 11):
        raise ValueError("telefone deve ter 10 ou 11 dígitos")
    if validar_cpf(documento):
        tipo, doc = TipoPessoa.PF, formatar_cpf(documento)
    elif validar_cnpj(documento):
        tipo, doc = TipoPessoa.PJ, formatar_cnpj(documento)
    else:
        raise ValueError("documento inválido (CPF ou CNPJ)")
    return Cliente(id, tipo, nome, doc, email.lower(), tel)


class CadastroClientes:
    def __init__(self) -> None:
        self._por_id: dict[int, Cliente] = {}
        self._por_doc: dict[str, int] = {}
        self._proximo = 1

    def cadastrar(self, nome: str, documento: str, email: str = "", telefone: str = "") -> Cliente:
        cliente = criar_cliente(self._proximo, nome, documento, email, telefone)
        if cliente.documento in self._por_doc:
            raise ValueError("documento já cadastrado")
        self._por_id[cliente.id] = cliente
        self._por_doc[cliente.documento] = cliente.id
        self._proximo += 1
        return cliente

    def obter(self, id: int) -> Cliente:
        if id not in self._por_id:
            raise KeyError(f"cliente {id} não encontrado")
        return self._por_id[id]

    def buscar_documento(self, documento: str) -> Cliente | None:
        d = _digitos(documento)
        for doc, cid in self._por_doc.items():
            if _digitos(doc) == d:
                return self._por_id[cid]
        return None

    def buscar_nome(self, trecho: str) -> list[Cliente]:
        t = trecho.casefold()
        return sorted((c for c in self._por_id.values() if t in c.nome.casefold()), key=lambda c: c.nome)

    def remover(self, id: int) -> None:
        c = self.obter(id)
        del self._por_id[id]
        del self._por_doc[c.documento]

    def __len__(self) -> int:
        return len(self._por_id)
