"""Mensagens DNS (RFC 1035): cabeçalho, perguntas, registros e compressão de nomes."""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

TIPO_A, TIPO_NS, TIPO_CNAME, TIPO_TXT, TIPO_AAAA = 1, 2, 5, 16, 28
CLASSE_IN = 1


@dataclass
class Pergunta:
    nome: str
    tipo: int = TIPO_A
    classe: int = CLASSE_IN


@dataclass
class Registro:
    nome: str
    tipo: int
    ttl: int
    dados: bytes | str  # A/AAAA: bytes crus; CNAME/NS: nome; TXT: str
    classe: int = CLASSE_IN


@dataclass
class Mensagem:
    id: int
    flags: int = 0x0100  # RD
    perguntas: list[Pergunta] = field(default_factory=list)
    respostas: list[Registro] = field(default_factory=list)
    autoridade: list[Registro] = field(default_factory=list)
    adicionais: list[Registro] = field(default_factory=list)

    @property
    def eh_resposta(self) -> bool:
        return bool(self.flags & 0x8000)

    @property
    def rcode(self) -> int:
        return self.flags & 0x000F


def _rotulos(nome: str) -> list[str]:
    nome = nome.rstrip(".")
    if not nome:
        return []
    rot = nome.split(".")
    for r in rot:
        if not r or len(r.encode("ascii")) > 63:
            raise ValueError(f"rótulo inválido: {r!r}")
    return rot


def codificar_nome(nome: str, saida: bytearray | None = None,
                   tabela: dict[str, int] | None = None) -> bytes:
    """Codifica um nome; com `tabela` usa ponteiros de compressão.

    `saida` é a mensagem em construção (os offsets dos ponteiros são relativos a ela).
    """
    rot = _rotulos(nome)
    base = len(saida) if saida is not None else 0
    out = bytearray()
    for i in range(len(rot)):
        sufixo = ".".join(rot[i:]).lower()
        if tabela is not None and sufixo in tabela:
            out += struct.pack("!H", 0xC000 | tabela[sufixo])
            return bytes(out)
        if tabela is not None and base + len(out) < 0x4000:
            tabela[sufixo] = base + len(out)
        r = rot[i].encode("ascii")
        out += bytes([len(r)]) + r
    out.append(0)
    return bytes(out)


def decodificar_nome(msg: bytes, pos: int) -> tuple[str, int]:
    """Lê um nome em `pos`; devolve (nome, posição após o nome no fluxo original)."""
    rot: list[str] = []
    fim = -1
    saltos = 0
    while True:
        if pos >= len(msg):
            raise ValueError("nome truncado")
        n = msg[pos]
        if n == 0:
            pos += 1
            break
        if n & 0xC0 == 0xC0:
            if pos + 1 >= len(msg):
                raise ValueError("ponteiro truncado")
            if fim < 0:
                fim = pos + 2
            saltos += 1
            if saltos > 64:
                raise ValueError("laço de compressão")
            pos = ((n & 0x3F) << 8) | msg[pos + 1]
            continue
        if n & 0xC0:
            raise ValueError("tipo de rótulo não suportado")
        if pos + 1 + n > len(msg):
            raise ValueError("rótulo truncado")
        rot.append(msg[pos + 1:pos + 1 + n].decode("ascii"))
        pos += 1 + n
    return ".".join(rot), (fim if fim >= 0 else pos)


def _rdata(r: Registro, buf: bytearray, tabela: dict[str, int]) -> bytes:
    if r.tipo in (TIPO_CNAME, TIPO_NS) and isinstance(r.dados, str):
        return codificar_nome(r.dados, buf, tabela)
    if r.tipo == TIPO_TXT and isinstance(r.dados, str):
        b = r.dados.encode("utf-8")
        return b"".join(bytes([len(b[i:i + 255])]) + b[i:i + 255] for i in range(0, len(b), 255)) or b"\x00"
    if isinstance(r.dados, bytes):
        return r.dados
    raise ValueError("dados incompatíveis com o tipo")


def serializar(m: Mensagem, comprimir: bool = True) -> bytes:
    buf = bytearray(struct.pack("!HHHHHH", m.id, m.flags, len(m.perguntas),
                                len(m.respostas), len(m.autoridade), len(m.adicionais)))
    tabela: dict[str, int] | None = {} if comprimir else None
    for p in m.perguntas:
        buf += codificar_nome(p.nome, buf, tabela)
        buf += struct.pack("!HH", p.tipo, p.classe)
    for r in m.respostas + m.autoridade + m.adicionais:
        buf += codificar_nome(r.nome, buf, tabela)
        buf += struct.pack("!HHI", r.tipo, r.classe, r.ttl)
        pos_len = len(buf)
        buf += b"\x00\x00"  # RDLENGTH provisório
        buf += _rdata_com_tabela(r, buf, tabela)
        buf[pos_len:pos_len + 2] = struct.pack("!H", len(buf) - pos_len - 2)
    return bytes(buf)


def _rdata_com_tabela(r: Registro, buf: bytearray, tabela: dict[str, int] | None) -> bytes:
    if tabela is None and r.tipo in (TIPO_CNAME, TIPO_NS) and isinstance(r.dados, str):
        return codificar_nome(r.dados)
    return _rdata(r, buf, tabela if tabela is not None else {})


def _ler_registro(msg: bytes, pos: int) -> tuple[Registro, int]:
    nome, pos = decodificar_nome(msg, pos)
    if pos + 10 > len(msg):
        raise ValueError("registro truncado")
    tipo, classe, ttl, rdlen = struct.unpack("!HHIH", msg[pos:pos + 10])
    pos += 10
    if pos + rdlen > len(msg):
        raise ValueError("RDATA truncado")
    cru = msg[pos:pos + rdlen]
    dados: bytes | str = cru
    if tipo in (TIPO_CNAME, TIPO_NS):
        dados, _ = decodificar_nome(msg, pos)
    elif tipo == TIPO_TXT:
        partes, i = [], 0
        while i < len(cru):
            n = cru[i]
            partes.append(cru[i + 1:i + 1 + n])
            i += 1 + n
        dados = b"".join(partes).decode("utf-8")
    return Registro(nome, tipo, ttl, dados, classe), pos + rdlen


def parse(msg: bytes) -> Mensagem:
    if len(msg) < 12:
        raise ValueError("mensagem menor que o cabeçalho")
    ident, flags, qd, an, ns, ar = struct.unpack("!HHHHHH", msg[:12])
    m = Mensagem(ident, flags)
    pos = 12
    for _ in range(qd):
        nome, pos = decodificar_nome(msg, pos)
        if pos + 4 > len(msg):
            raise ValueError("pergunta truncada")
        tipo, classe = struct.unpack("!HH", msg[pos:pos + 4])
        pos += 4
        m.perguntas.append(Pergunta(nome, tipo, classe))
    for destino, qtd in ((m.respostas, an), (m.autoridade, ns), (m.adicionais, ar)):
        for _ in range(qtd):
            r, pos = _ler_registro(msg, pos)
            destino.append(r)
    return m


def consulta(ident: int, nome: str, tipo: int = TIPO_A) -> bytes:
    return serializar(Mensagem(ident, 0x0100, [Pergunta(nome, tipo)]))
