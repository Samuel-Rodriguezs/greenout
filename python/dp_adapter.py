"""Adapter: gateway de pagamento legado (centavos/dict) para interface moderna."""
from __future__ import annotations

from decimal import Decimal


class GatewayLegado:
    """API antiga: valores em centavos inteiros, retorno em dict."""

    def __init__(self) -> None:
        self.transacoes: list[dict] = []

    def cobrar(self, centavos: int, codigo_moeda: str) -> dict:
        if centavos <= 0:
            return {"status": "ERRO", "id": None}
        tid = f"TX{len(self.transacoes) + 1:04d}"
        self.transacoes.append({"id": tid, "centavos": centavos,
                                "moeda": codigo_moeda})
        return {"status": "OK", "id": tid}


class AdaptadorGateway:
    def __init__(self, legado: GatewayLegado) -> None:
        self._legado = legado

    def pagar(self, valor: Decimal, moeda: str) -> str:
        centavos = int((valor * 100).to_integral_value())
        resposta = self._legado.cobrar(centavos, moeda.upper())
        if resposta["status"] != "OK":
            raise ValueError("pagamento recusado")
        return resposta["id"]
