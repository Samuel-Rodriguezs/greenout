import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_adapter import AdaptadorGateway, GatewayLegado


class TestAdapter(unittest.TestCase):
    def test_converte_para_centavos(self):
        g = GatewayLegado()
        a = AdaptadorGateway(g)
        tid = a.pagar(Decimal("12.34"), "brl")
        self.assertEqual(tid, "TX0001")
        self.assertEqual(g.transacoes[0]["centavos"], 1234)
        self.assertEqual(g.transacoes[0]["moeda"], "BRL")

    def test_recusa(self):
        with self.assertRaises(ValueError):
            AdaptadorGateway(GatewayLegado()).pagar(Decimal("0"), "BRL")

    def test_ids_sequenciais(self):
        a = AdaptadorGateway(GatewayLegado())
        a.pagar(Decimal("1"), "USD")
        self.assertEqual(a.pagar(Decimal("2"), "USD"), "TX0002")


if __name__ == "__main__":
    unittest.main()
