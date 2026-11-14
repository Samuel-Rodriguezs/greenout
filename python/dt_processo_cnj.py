"""Número único de processo do CNJ (Res. 65/2008): NNNNNNN-DD.AAAA.J.TR.OOOO, DV por módulo 97."""
from __future__ import annotations

import re
from dataclasses import dataclass

SEGMENTOS = {
    1: "Supremo Tribunal Federal",
    2: "Conselho Nacional de Justiça",
    3: "Superior Tribunal de Justiça",
    4: "Justiça Federal",
    5: "Justiça do Trabalho",
    6: "Justiça Eleitoral",
    7: "Justiça Militar da União",
    8: "Justiça dos Estados e do DF e Territórios",
    9: "Justiça Militar Estadual",
}

_FORMATADO = re.compile(r"^(\d{7})-(\d{2})\.(\d{4})\.(\d)\.(\d{2})\.(\d{4})$")


@dataclass(frozen=True)
class ProcessoCnj:
    sequencial: str
    dv: str
    ano: str
    segmento: int
    tribunal: str
    origem: str

    @property
    def nome_segmento(self) -> str:
        return SEGMENTOS[self.segmento]

    def __str__(self) -> str:
        return f"{self.sequencial}-{self.dv}.{self.ano}.{self.segmento}.{self.tribunal}.{self.origem}"


def _normalizar(numero: str) -> str:
    return re.sub(r"[.\-\s]", "", numero)


def calcular_dv(sequencial: str, ano: str, segmento: str, tribunal: str, origem: str) -> str:
    """DV = 98 - ((NNNNNNN AAAA J TR OOOO 00) mod 97), com dois dígitos."""
    corpo = f"{sequencial}{ano}{segmento}{tribunal}{origem}"
    if not re.fullmatch(r"\d{7}\d{4}\d\d{2}\d{4}", corpo):
        raise ValueError("campos com tamanho inválido (7, 4, 1, 2 e 4 dígitos)")
    return f"{98 - int(corpo + '00') % 97:02d}"


def parse_processo(numero: str) -> ProcessoCnj:
    """Lê um número (com ou sem máscara). Levanta ValueError se o formato ou o DV estiverem errados."""
    n = _normalizar(numero)
    if not re.fullmatch(r"\d{20}", n):
        raise ValueError("o número do processo deve ter 20 dígitos")
    sequencial, dv, ano, seg, tr, origem = n[:7], n[7:9], n[9:13], n[13], n[14:16], n[16:]
    if not 1 <= int(seg) <= 9:
        raise ValueError("segmento do Judiciário inválido")
    if calcular_dv(sequencial, ano, seg, tr, origem) != dv:
        raise ValueError("dígito verificador não confere")
    return ProcessoCnj(sequencial, dv, ano, int(seg), tr, origem)


def validar_processo(numero: str) -> bool:
    try:
        parse_processo(numero)
    except ValueError:
        return False
    return True


def formatar_processo(numero: str) -> str:
    return str(parse_processo(numero))


def montar_processo(sequencial: int, ano: int, segmento: int, tribunal: int, origem: int) -> str:
    """Gera o número formatado, calculando o DV."""
    seq, a, seg, tr, o = f"{sequencial:07d}", f"{ano:04d}", str(segmento), f"{tribunal:02d}", f"{origem:04d}"
    dv = calcular_dv(seq, a, seg, tr, o)
    return str(parse_processo(f"{seq}{dv}{a}{seg}{tr}{o}"))
