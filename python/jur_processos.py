"""Processos judiciais: número CNJ, partes, fase e valor da causa."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal
from enum import Enum

from dt_processo_cnj import formatar_processo, parse_processo


class Fase(Enum):
    CONHECIMENTO = "conhecimento"
    RECURSAL = "recursal"
    EXECUCAO = "execucao"
    ENCERRADO = "encerrado"


class Polo(Enum):
    ATIVO = "ativo"
    PASSIVO = "passivo"


@dataclass(frozen=True)
class Parte:
    nome: str
    polo: Polo
    cliente_id: int | None = None


@dataclass(frozen=True)
class Processo:
    numero: str
    area: str
    advogado: str
    valor_causa: Decimal
    fase: Fase = Fase.CONHECIMENTO
    partes: tuple[Parte, ...] = field(default_factory=tuple)

    @property
    def tribunal(self) -> str:
        return parse_processo(self.numero).tribunal

    def partes_do_polo(self, polo: Polo) -> list[Parte]:
        return [p for p in self.partes if p.polo == polo]

    def nosso_cliente(self) -> list[Parte]:
        return [p for p in self.partes if p.cliente_id is not None]


_ORDEM = [Fase.CONHECIMENTO, Fase.RECURSAL, Fase.EXECUCAO, Fase.ENCERRADO]


def criar_processo(numero: str, area: str, advogado: str, valor_causa: Decimal | str | int) -> Processo:
    valor = Decimal(str(valor_causa))
    if valor < 0:
        raise ValueError("valor da causa não pode ser negativo")
    if not area.strip() or not advogado.strip():
        raise ValueError("área e advogado são obrigatórios")
    return Processo(formatar_processo(numero), area.strip().lower(), advogado.strip(), valor)


def adicionar_parte(p: Processo, parte: Parte) -> Processo:
    if not parte.nome.strip():
        raise ValueError("nome da parte é obrigatório")
    if any(x.nome.casefold() == parte.nome.casefold() and x.polo == parte.polo for x in p.partes):
        raise ValueError("parte já cadastrada neste polo")
    if any(x.nome.casefold() == parte.nome.casefold() for x in p.partes):
        raise ValueError("a mesma parte não pode estar nos dois polos")
    return replace(p, partes=p.partes + (parte,))


def avancar_fase(p: Processo, nova: Fase) -> Processo:
    """Fases só avançam; EXECUCAO pode vir direto do conhecimento (sem recurso)."""
    if _ORDEM.index(nova) <= _ORDEM.index(p.fase):
        raise ValueError(f"não é possível ir de {p.fase.value} para {nova.value}")
    return replace(p, fase=nova)
