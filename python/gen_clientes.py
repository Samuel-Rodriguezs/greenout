"""Perfis completos de clientes fictícios, gerados em lote a partir de uma seed."""
from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from datetime import date

from gen_documentos import gerar_cpf
from gen_email import email_do_nome
from gen_endereco import Endereco, gerar_endereco
from gen_nascimento import gerar_nascimento
from gen_nomes import gerar_nome_completo
from gen_telefone import gerar_celular


@dataclass(frozen=True)
class Cliente:
    id: int
    nome: str
    genero: str
    cpf: str
    email: str
    telefone: str
    nascimento: date
    endereco: Endereco

    def como_dict(self) -> dict:
        d = asdict(self)
        d["nascimento"] = self.nascimento.isoformat()
        return d


def gerar_cliente(rng: random.Random, id_: int, referencia: date) -> Cliente:
    genero = rng.choice("MF")
    nome = gerar_nome_completo(rng, genero)
    return Cliente(
        id=id_,
        nome=nome,
        genero=genero,
        cpf=gerar_cpf(rng),
        email=email_do_nome(nome, rng),
        telefone=gerar_celular(rng),
        nascimento=gerar_nascimento(rng, referencia, 18, 85),
        endereco=gerar_endereco(rng),
    )


def gerar_clientes(seed: int, n: int, referencia: date) -> list[Cliente]:
    """Lote com CPFs e e-mails únicos; ids sequenciais a partir de 1."""
    rng = random.Random(seed)
    cpfs: set[str] = set()
    emails: set[str] = set()
    saida: list[Cliente] = []
    while len(saida) < n:
        c = gerar_cliente(rng, len(saida) + 1, referencia)
        if c.cpf in cpfs or c.email in emails:
            continue
        cpfs.add(c.cpf)
        emails.add(c.email)
        saida.append(c)
    return saida
