"""Parser de CSV com campos entre aspas (RFC 4180): vírgulas, quebras de linha e "" escapado."""
from __future__ import annotations


class ErroCSV(Exception):
    """Erro de sintaxe no CSV."""


def analisar(texto: str, separador: str = ",") -> list[list[str]]:
    """Converte texto CSV em lista de linhas (listas de campos)."""
    if len(separador) != 1 or separador in '"\r\n':
        raise ValueError("separador inválido")
    linhas: list[list[str]] = []
    campo: list[str] = []
    linha: list[str] = []
    i, n = 0, len(texto)
    tem_conteudo = False  # linha corrente tem algo (campo ou separador)
    while i < n:
        c = texto[i]
        if c == '"' and not campo:
            # campo entre aspas
            i += 1
            while True:
                if i >= n:
                    raise ErroCSV("aspas não fechadas")
                if texto[i] == '"':
                    if i + 1 < n and texto[i + 1] == '"':
                        campo.append('"')
                        i += 2
                        continue
                    i += 1
                    break
                campo.append(texto[i])
                i += 1
            if i < n and texto[i] not in (separador, "\r", "\n"):
                raise ErroCSV(f"caractere inesperado {texto[i]!r} após aspas de fechamento")
            tem_conteudo = True
        elif c == '"':
            raise ErroCSV("aspas no meio de campo sem aspas")
        elif c == separador:
            linha.append("".join(campo))
            campo = []
            tem_conteudo = True
            i += 1
        elif c in "\r\n":
            if c == "\r" and i + 1 < n and texto[i + 1] == "\n":
                i += 1
            i += 1
            if tem_conteudo or campo or linha:
                linha.append("".join(campo))
                linhas.append(linha)
            else:
                linhas.append([""])
            campo, linha, tem_conteudo = [], [], False
        else:
            campo.append(c)
            tem_conteudo = True
            i += 1
    if tem_conteudo or campo or linha:
        linha.append("".join(campo))
        linhas.append(linha)
    return linhas


def analisar_dicts(texto: str, separador: str = ",") -> list[dict[str, str]]:
    """Usa a primeira linha como cabeçalho; exige o mesmo número de colunas."""
    linhas = [l for l in analisar(texto, separador) if l != [""]]
    if not linhas:
        return []
    cab = linhas[0]
    saida = []
    for k, l in enumerate(linhas[1:], 2):
        if len(l) != len(cab):
            raise ErroCSV(f"linha {k}: {len(l)} campos, esperado {len(cab)}")
        saida.append(dict(zip(cab, l)))
    return saida


def gerar(linhas: list[list[str]], separador: str = ",") -> str:
    """Serializa linhas em CSV, citando campos quando necessário."""
    def cita(c: str) -> str:
        if any(x in c for x in (separador, '"', "\n", "\r")):
            return '"' + c.replace('"', '""') + '"'
        return c
    return "\n".join(separador.join(cita(c) for c in l) for l in linhas)
