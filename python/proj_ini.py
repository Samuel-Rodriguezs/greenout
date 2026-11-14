"""Parser de arquivos .ini (secoes, chaves, comentarios, conversao de tipos)."""
from typing import Dict, Union

Valor = Union[bool, int, float, str]
Config = Dict[str, Dict[str, Valor]]


class ErroIni(Exception):
    pass


def converter(texto: str) -> Valor:
    baixo = texto.lower()
    if baixo in ("true", "yes", "on"):
        return True
    if baixo in ("false", "no", "off"):
        return False
    for tipo in (int, float):
        try:
            return tipo(texto)
        except ValueError:
            pass
    if len(texto) >= 2 and texto[0] == texto[-1] and texto[0] in "\"'":
        return texto[1:-1]
    return texto


def parse_ini(conteudo: str) -> Config:
    config: Config = {"": {}}
    secao = ""
    for n, bruta in enumerate(conteudo.splitlines(), start=1):
        linha = bruta.strip()
        if not linha or linha[0] in ";#":
            continue
        if linha.startswith("["):
            if not linha.endswith("]") or len(linha) < 3:
                raise ErroIni(f"linha {n}: secao invalida")
            secao = linha[1:-1].strip()
            config.setdefault(secao, {})
        elif "=" in linha:
            chave, _, valor = linha.partition("=")
            chave = chave.strip()
            if not chave:
                raise ErroIni(f"linha {n}: chave vazia")
            config[secao][chave] = converter(valor.strip())
        else:
            raise ErroIni(f"linha {n}: sintaxe invalida")
    if not config[""]:
        del config[""]
    return config
