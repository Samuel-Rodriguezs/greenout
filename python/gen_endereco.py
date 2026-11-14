"""CEPs e endereços brasileiros fictícios."""
from __future__ import annotations

import random
from dataclasses import dataclass

# (UF, cidade, primeiro dígito do CEP coerente com a região postal)
CIDADES: tuple[tuple[str, str, int], ...] = (
    ("SP", "São Paulo", 0), ("SP", "Campinas", 1), ("RJ", "Niterói", 2),
    ("ES", "Vitória", 2), ("MG", "Belo Horizonte", 3), ("BA", "Salvador", 4),
    ("PE", "Recife", 5), ("CE", "Fortaleza", 6), ("DF", "Brasília", 7),
    ("GO", "Goiânia", 7), ("PR", "Curitiba", 8), ("SC", "Florianópolis", 8),
    ("RS", "Porto Alegre", 9),
)
TIPOS_LOGRADOURO: tuple[str, ...] = ("Rua", "Avenida", "Travessa", "Alameda", "Praça")
NOMES_LOGRADOURO: tuple[str, ...] = (
    "das Flores", "Sete de Setembro", "da Liberdade", "dos Ipês", "Quinze de Novembro",
    "das Acácias", "Santos Dumont", "do Comércio", "São José", "da Paz",
)
BAIRROS: tuple[str, ...] = ("Centro", "Jardim América", "Vila Nova", "Boa Vista", "Santa Cruz", "Bela Vista")
COMPLEMENTOS: tuple[str, ...] = ("", "", "Apto 101", "Bloco B", "Sala 3", "Casa 2")


@dataclass(frozen=True)
class Endereco:
    logradouro: str
    numero: int
    complemento: str
    bairro: str
    cidade: str
    uf: str
    cep: str

    def formatado(self) -> str:
        comp = f", {self.complemento}" if self.complemento else ""
        return (
            f"{self.logradouro}, {self.numero}{comp} - {self.bairro}, "
            f"{self.cidade}/{self.uf} - CEP {self.cep}"
        )


def gerar_cep(rng: random.Random, regiao: int | None = None, formatado: bool = True) -> str:
    """CEP de 8 dígitos (nunca 00000-000). `regiao` fixa o primeiro dígito."""
    if regiao is not None and not 0 <= regiao <= 9:
        raise ValueError("região deve estar entre 0 e 9")
    while True:
        d = regiao if regiao is not None else rng.randint(0, 9)
        s = f"{d}{rng.randint(0, 9_999_999):07d}"
        if s != "00000000":
            break
    return f"{s[:5]}-{s[5:]}" if formatado else s


def gerar_endereco(rng: random.Random) -> Endereco:
    uf, cidade, regiao = rng.choice(CIDADES)
    return Endereco(
        logradouro=f"{rng.choice(TIPOS_LOGRADOURO)} {rng.choice(NOMES_LOGRADOURO)}",
        numero=rng.randint(1, 9999),
        complemento=rng.choice(COMPLEMENTOS),
        bairro=rng.choice(BAIRROS),
        cidade=cidade,
        uf=uf,
        cep=gerar_cep(rng, regiao),
    )


def gerar_lote(rng: random.Random, n: int) -> list[Endereco]:
    return [gerar_endereco(rng) for _ in range(n)]
