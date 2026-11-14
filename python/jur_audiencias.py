"""Agenda de audiências com detecção de conflito (duplicidade, advogado e local)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class Audiencia:
    processo: str
    inicio: datetime
    duracao_min: int
    local: str
    advogado: str
    tipo: str = "instrução"

    def __post_init__(self) -> None:
        if self.duracao_min <= 0:
            raise ValueError("duração deve ser positiva")

    @property
    def fim(self) -> datetime:
        return self.inicio + timedelta(minutes=self.duracao_min)

    def sobrepoe(self, outra: "Audiencia") -> bool:
        return self.inicio < outra.fim and outra.inicio < self.fim


class Agenda:
    def __init__(self, folga_min: int = 0) -> None:
        """folga_min: intervalo mínimo exigido entre audiências do mesmo advogado."""
        self.folga = timedelta(minutes=folga_min)
        self._itens: list[Audiencia] = []

    def conflitos(self, nova: Audiencia) -> list[tuple[Audiencia, str]]:
        res: list[tuple[Audiencia, str]] = []
        for a in self._itens:
            if a.processo == nova.processo and a.inicio == nova.inicio:
                res.append((a, "duplicada"))
            elif a.advogado == nova.advogado and a.inicio - self.folga < nova.fim and nova.inicio < a.fim + self.folga:
                res.append((a, "advogado"))
            elif a.local == nova.local and a.sobrepoe(nova):
                res.append((a, "local"))
        return res

    def agendar(self, nova: Audiencia) -> None:
        c = self.conflitos(nova)
        if c:
            raise ValueError(f"conflito de {c[0][1]} com audiência do processo {c[0][0].processo}")
        self._itens.append(nova)
        self._itens.sort(key=lambda a: a.inicio)

    def cancelar(self, processo: str, inicio: datetime) -> bool:
        antes = len(self._itens)
        self._itens = [a for a in self._itens if not (a.processo == processo and a.inicio == inicio)]
        return len(self._itens) < antes

    def do_dia(self, dia: date) -> list[Audiencia]:
        return [a for a in self._itens if a.inicio.date() == dia]

    def do_advogado(self, advogado: str) -> list[Audiencia]:
        return [a for a in self._itens if a.advogado == advogado]

    def proxima(self, agora: datetime) -> Audiencia | None:
        return next((a for a in self._itens if a.inicio >= agora), None)

    def horarios_livres(self, dia: date, advogado: str, duracao_min: int,
                        abre: int = 9, fecha: int = 18, passo_min: int = 30) -> list[datetime]:
        """Inícios possíveis no dia, sem conflito para o advogado."""
        livres: list[datetime] = []
        t = datetime(dia.year, dia.month, dia.day, abre)
        limite = datetime(dia.year, dia.month, dia.day, fecha)
        while t + timedelta(minutes=duracao_min) <= limite:
            teste = Audiencia("_", t, duracao_min, "_livre", advogado)
            if not any(motivo == "advogado" for _, motivo in self.conflitos(teste)):
                livres.append(t)
            t += timedelta(minutes=passo_min)
        return livres

    def __len__(self) -> int:
        return len(self._itens)
