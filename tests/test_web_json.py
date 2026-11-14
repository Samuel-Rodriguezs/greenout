import json
import sys
import unittest
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_json import dumps, loads


class Cor(Enum):
    VERMELHO = "vermelho"


@dataclass
class Item:
    nome: str
    preco: Decimal


class TestWebJson(unittest.TestCase):
    def test_simples(self):
        d = datetime(2024, 5, 1, 10, 30, tzinfo=timezone.utc)
        s = dumps({"d": d, "dt": date(2024, 5, 1), "t": time(8, 5), "p": Decimal("1.10")})
        self.assertEqual(json.loads(s), {"d": "2024-05-01T10:30:00+00:00", "dt": "2024-05-01",
                                         "t": "08:05:00", "p": "1.10"})

    def test_outros_tipos(self):
        u = uuid.UUID("12345678-1234-5678-1234-567812345678")
        s = json.loads(dumps({"u": u, "c": Cor.VERMELHO, "s": {3, 1, 2}, "b": b"\x00\xff",
                              "i": Item("x", Decimal("2.5"))}))
        self.assertEqual(s["u"], str(u))
        self.assertEqual(s["c"], "vermelho")
        self.assertEqual(s["s"], [1, 2, 3])
        self.assertEqual(s["b"], "AP8=")
        self.assertEqual(s["i"], {"nome": "x", "preco": "2.5"})

    def test_roundtrip_marcado(self):
        original = {"d": datetime(2024, 1, 2, 3, 4, 5), "dt": date(2020, 2, 29),
                    "t": time(1, 2, 3), "p": Decimal("0.1000"),
                    "u": uuid.uuid4(), "s": {1, 2}, "b": b"abc", "lista": [Decimal("1")]}
        self.assertEqual(loads(dumps(original, marcado=True)), original)

    def test_decimal_preserva_precisao(self):
        d = Decimal("12345678901234567890.123456789")
        self.assertEqual(loads(dumps(d, marcado=True)), d)

    def test_tipo_nao_suportado(self):
        with self.assertRaises(TypeError):
            dumps({"x": object()})

    def test_decimal_nao_finito(self):
        with self.assertRaises(ValueError):
            dumps(Decimal("NaN"))

    def test_loads_invalido(self):
        with self.assertRaises(ValueError):
            loads('{"__tipo__": "datetime", "valor": "ontem"}')
        with self.assertRaises(ValueError):
            loads('{"__tipo__": "xyz", "valor": 1}')

    def test_dict_comum_com_chave_tipo_nao_e_alterado(self):
        self.assertEqual(loads('{"__tipo__": "x", "outro": 1}'), {"__tipo__": "x", "outro": 1})

    def test_kwargs_e_unicode(self):
        self.assertEqual(dumps({"a": "é"}, sort_keys=True), '{"a": "é"}')


if __name__ == "__main__":
    unittest.main()
