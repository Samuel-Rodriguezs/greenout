"""Parser XML simples (tags, atributos, texto, CDATA, comentários) para árvore."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


class ErroXml(ValueError):
    """XML malformado."""


@dataclass
class No:
    tag: str
    atributos: dict[str, str] = field(default_factory=dict)
    filhos: list["No"] = field(default_factory=list)
    texto: str = ""

    def buscar(self, tag: str) -> list["No"]:
        """Todos os descendentes (inclusive este) com a tag dada."""
        achados = [self] if self.tag == tag else []
        for f in self.filhos:
            achados.extend(f.buscar(tag))
        return achados

    def texto_total(self) -> str:
        return self.texto + "".join(f.texto_total() for f in self.filhos)


_ENTIDADES = {"lt": "<", "gt": ">", "amp": "&", "quot": '"', "apos": "'"}
_NOME = r"[A-Za-z_:][\w:.\-]*"


def _decodificar(s: str) -> str:
    def troca(m: re.Match[str]) -> str:
        e = m.group(1)
        if e.startswith("#x"):
            return chr(int(e[2:], 16))
        if e.startswith("#"):
            return chr(int(e[1:]))
        if e in _ENTIDADES:
            return _ENTIDADES[e]
        raise ErroXml(f"entidade desconhecida: &{e};")
    return re.sub(r"&(#x[0-9A-Fa-f]+|#\d+|\w+);", troca, s)


def _escapar(s: str, aspas: bool = False) -> str:
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace('"', "&quot;") if aspas else s


def _atributos(s: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    pos = 0
    padrao = re.compile(rf"\s*({_NOME})\s*=\s*(\"([^\"]*)\"|'([^']*)')")
    while s[pos:].strip():
        m = padrao.match(s, pos)
        if not m:
            raise ErroXml(f"atributo inválido: {s[pos:].strip()!r}")
        nome = m.group(1)
        if nome in attrs:
            raise ErroXml(f"atributo duplicado: {nome}")
        bruto = m.group(3) if m.group(3) is not None else m.group(4)
        attrs[nome] = _decodificar(bruto)
        pos = m.end()
    return attrs


def parse(xml: str) -> No:
    """Converte um documento XML em uma árvore de No."""
    pilha: list[No] = []
    raiz: No | None = None
    i = 0
    n = len(xml)
    while i < n:
        if xml[i] != "<":
            j = xml.find("<", i)
            j = n if j == -1 else j
            txt = xml[i:j]
            if pilha:
                pilha[-1].texto += _decodificar(txt)
            elif txt.strip():
                raise ErroXml("texto fora do elemento raiz")
            i = j
            continue
        if xml.startswith("<!--", i):
            fim = xml.find("-->", i + 4)
            if fim == -1:
                raise ErroXml("comentário não fechado")
            i = fim + 3
        elif xml.startswith("<![CDATA[", i):
            fim = xml.find("]]>", i)
            if fim == -1 or not pilha:
                raise ErroXml("CDATA inválido")
            pilha[-1].texto += xml[i + 9:fim]
            i = fim + 3
        elif xml.startswith("<?", i):
            fim = xml.find("?>", i)
            if fim == -1:
                raise ErroXml("instrução não fechada")
            i = fim + 2
        elif xml.startswith("<!", i):
            fim = xml.find(">", i)
            if fim == -1:
                raise ErroXml("declaração não fechada")
            i = fim + 1
        elif xml.startswith("</", i):
            fim = xml.find(">", i)
            if fim == -1:
                raise ErroXml("tag de fechamento não terminada")
            nome = xml[i + 2:fim].strip()
            if not pilha or pilha[-1].tag != nome:
                esperado = pilha[-1].tag if pilha else "nenhuma"
                raise ErroXml(f"fechamento </{nome}> inesperado (aberta: {esperado})")
            pilha.pop()
            i = fim + 1
        else:
            m = re.compile(rf"<({_NOME})((?:\s+{_NOME}\s*=\s*(?:\"[^\"]*\"|'[^']*'))*)\s*(/?)>").match(xml, i)
            if not m:
                raise ErroXml(f"tag inválida perto de: {xml[i:i + 20]!r}")
            no = No(m.group(1), _atributos(m.group(2)))
            if pilha:
                pilha[-1].filhos.append(no)
            elif raiz is not None:
                raise ErroXml("mais de um elemento raiz")
            else:
                raiz = no
            if not m.group(3):
                pilha.append(no)
            i = m.end()
    if pilha:
        raise ErroXml(f"tag não fechada: <{pilha[-1].tag}>")
    if raiz is None:
        raise ErroXml("documento sem elemento raiz")
    return raiz


def serializar(no: No) -> str:
    """Converte a árvore de volta para texto XML (sem indentação)."""
    attrs = "".join(f' {k}="{_escapar(v, True)}"' for k, v in no.atributos.items())
    if not no.filhos and not no.texto:
        return f"<{no.tag}{attrs}/>"
    corpo = _escapar(no.texto) + "".join(serializar(f) for f in no.filhos)
    return f"<{no.tag}{attrs}>{corpo}</{no.tag}>"
