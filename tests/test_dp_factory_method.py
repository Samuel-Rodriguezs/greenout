import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_factory_method import (ExportadorCsv, ExportadorJson, Relatorio,
                               RelatorioCsv, RelatorioJson)

DADOS = [{"nome": "Ana", "nota": 9}, {"nome": "Bia", "nota": 8}]


class TestFactoryMethod(unittest.TestCase):
    def test_json(self):
        r = RelatorioJson(DADOS)
        self.assertIsInstance(r.criar_exportador(), ExportadorJson)
        self.assertIn('"Ana"', r.gerar())

    def test_csv(self):
        r = RelatorioCsv(DADOS)
        self.assertIsInstance(r.criar_exportador(), ExportadorCsv)
        self.assertEqual(r.gerar(), "nome,nota\nAna,9\nBia,8")

    def test_csv_vazio(self):
        self.assertEqual(RelatorioCsv([]).gerar(), "")

    def test_abstrata(self):
        with self.assertRaises(TypeError):
            Relatorio([])


if __name__ == "__main__":
    unittest.main()
