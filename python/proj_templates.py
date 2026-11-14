"""Mini-motor de templates com {{var}}, caminhos pontuados e filtros."""
import re
from typing import Any, Callable, Dict

FILTROS: Dict[str, Callable[[Any], Any]] = {
    "upper": lambda v: str(v).upper(),
    "lower": lambda v: str(v).lower(),
    "title": lambda v: str(v).title(),
    "len": lambda v: len(v),
}

_PADRAO = re.compile(r"\{\{\s*(.*?)\s*\}\}")


class ErroTemplate(Exception):
    pass


def _resolver(caminho: str, contexto: Dict[str, Any]) -> Any:
    atual: Any = contexto
    for parte in caminho.split("."):
        if isinstance(atual, dict) and parte in atual:
            atual = atual[parte]
        elif isinstance(atual, (list, tuple)) and parte.isdigit() and int(parte) < len(atual):
            atual = atual[int(parte)]
        else:
            raise ErroTemplate(f"variavel nao definida: {caminho}")
    return atual


def renderizar(template: str, contexto: Dict[str, Any]) -> str:
    def substituir(m: "re.Match[str]") -> str:
        expressao, *filtros = [p.strip() for p in m.group(1).split("|")]
        if not expressao:
            raise ErroTemplate("expressao vazia")
        valor = _resolver(expressao, contexto)
        for nome in filtros:
            if nome not in FILTROS:
                raise ErroTemplate(f"filtro desconhecido: {nome}")
            valor = FILTROS[nome](valor)
        return str(valor)

    return _PADRAO.sub(substituir, template)
