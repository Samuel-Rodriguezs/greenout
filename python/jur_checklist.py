"""Checklist de documentos por tipo de ação e controle de documentos faltantes."""
from __future__ import annotations

from dataclasses import dataclass, field

EXIGENCIAS: dict[str, dict[str, bool]] = {
    # documento -> obrigatório?
    "trabalhista": {"rg": True, "cpf": True, "ctps": True, "termo de rescisão": True,
                    "holerites": False, "procuração": True},
    "divorcio": {"rg": True, "cpf": True, "certidão de casamento": True, "procuração": True,
                 "certidão de nascimento dos filhos": False, "comprovante de residência": True},
    "consumidor": {"rg": True, "cpf": True, "comprovante de residência": True,
                   "contrato": True, "notas fiscais": False, "procuração": True},
}


def _norm(s: str) -> str:
    return " ".join(s.casefold().split())


@dataclass
class ChecklistProcesso:
    tipo_acao: str
    exigencias: dict[str, bool] = field(default_factory=dict)
    recebidos: set[str] = field(default_factory=set)

    def receber(self, documento: str) -> None:
        d = _norm(documento)
        if d not in self.exigencias:
            raise ValueError(f"documento não previsto para {self.tipo_acao}: {documento}")
        self.recebidos.add(d)

    def estornar(self, documento: str) -> None:
        self.recebidos.discard(_norm(documento))

    def faltantes(self, incluir_opcionais: bool = False) -> list[str]:
        return sorted(d for d, obrig in self.exigencias.items()
                      if d not in self.recebidos and (obrig or incluir_opcionais))

    def completo(self) -> bool:
        return not self.faltantes()

    def percentual(self) -> float:
        """Percentual dos documentos obrigatórios já recebidos."""
        obrig = [d for d, o in self.exigencias.items() if o]
        if not obrig:
            return 100.0
        return round(100 * sum(1 for d in obrig if d in self.recebidos) / len(obrig), 1)


def novo_checklist(tipo_acao: str, tabela: dict[str, dict[str, bool]] | None = None) -> ChecklistProcesso:
    tab = tabela if tabela is not None else EXIGENCIAS
    chave = _norm(tipo_acao)
    if chave not in tab:
        raise KeyError(f"tipo de ação sem checklist: {tipo_acao}")
    return ChecklistProcesso(chave, {_norm(d): o for d, o in tab[chave].items()})


def pendencias_gerais(checklists: dict[str, ChecklistProcesso]) -> dict[str, list[str]]:
    """Processo -> documentos obrigatórios faltantes, só dos que têm pendência."""
    return {p: c.faltantes() for p, c in sorted(checklists.items()) if c.faltantes()}
