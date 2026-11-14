"""Parser e formatador de FASTA."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Registro:
    id: str
    descricao: str
    sequencia: str


def parse(texto: str) -> list[Registro]:
    """Lê FASTA multi-registro; sequências em várias linhas são unidas."""
    regs: list[Registro] = []
    cab: str | None = None
    partes: list[str] = []

    def fechar() -> None:
        if cab is not None:
            id_, _, desc = cab.partition(" ")
            regs.append(Registro(id_, desc.strip(), "".join(partes)))

    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith(";"):
            continue
        if linha.startswith(">"):
            fechar()
            cab, partes = linha[1:].strip(), []
        else:
            if cab is None:
                raise ValueError("sequência antes do primeiro cabeçalho")
            partes.append(linha)
    fechar()
    return regs


def formatar(registros: list[Registro], largura: int = 60) -> str:
    if largura <= 0:
        raise ValueError("largura deve ser positiva")
    linhas = []
    for r in registros:
        linhas.append(f">{r.id} {r.descricao}".rstrip())
        s = r.sequencia
        linhas.extend(s[i : i + largura] for i in range(0, len(s), largura))
    return "\n".join(linhas) + ("\n" if linhas else "")
