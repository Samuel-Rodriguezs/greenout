"""Checkpoint sobre o WAL: grava páginas sujas, registra transações ativas e trunca o log.

O log só precisa manter, para a recuperação, os registros a partir do BEGIN da
transação ativa mais antiga (necessários para o undo); tudo antes disso já está
refletido no disco e em transações terminadas.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from bd_wal import BancoWAL, Disco


class BancoCheckpoint(BancoWAL):
    def __init__(self, caminho_log: str, disco: Optional[Disco] = None) -> None:
        super().__init__(caminho_log, disco)
        self.checkpoints = 0

    def _inicio_da_transacao(self, ultimo_lsn: int) -> int:
        atual = ultimo_lsn
        while True:
            r = self.log.obter(atual)
            if r["prev"] == 0:
                return r["lsn"]
            atual = r["prev"]

    def checkpoint(self, truncar: bool = True) -> int:
        """Devolve o número de registros descartados do log."""
        self.descarregar_tudo()  # sharp checkpoint: o disco reflete todo o cache
        lsn = self.log.anexar(tipo="CHECKPOINT", tx=0, prev=0, ativas=dict(self.txs))
        self.log.forcar()
        self.checkpoints += 1
        if not truncar:
            return 0
        corte = lsn
        for ultimo in self.txs.values():
            corte = min(corte, self._inicio_da_transacao(ultimo))
        mantidos = [r for r in self.log.duravel if r["lsn"] >= corte]
        descartados = len(self.log.duravel) - len(mantidos)
        temporario = self.log.caminho + ".tmp"
        with open(temporario, "w", encoding="utf-8") as f:
            for r in mantidos:
                f.write(json.dumps(r) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, self.log.caminho)  # troca atômica
        self.log.duravel = mantidos
        return descartados

    def crash(self) -> "BancoCheckpoint":
        return BancoCheckpoint(self.log.caminho, self.disco)
