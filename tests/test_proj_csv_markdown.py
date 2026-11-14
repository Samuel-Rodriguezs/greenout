import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_csv_markdown import csv_para_markdown


class TestCsvMarkdown(unittest.TestCase):
    def test_tabela_basica(self):
        saida = csv_para_markdown("nome,qtd\nmaca,10\npera,2")
        self.assertEqual(
            saida.splitlines(),
            [
                "| nome | qtd |",
                "| ---- | --: |",
                "| maca |  10 |",
                "| pera |   2 |",
            ],
        )

    def test_delimitador(self):
        saida = csv_para_markdown("a;b\nx;y", delimitador=";")
        self.assertEqual(saida.splitlines()[0], "| a   | b   |")

    def test_escapa_pipe_e_aspas(self):
        saida = csv_para_markdown('c\n"a|b"')
        self.assertIn("a\\|b", saida)

    def test_so_cabecalho(self):
        saida = csv_para_markdown("x,y")
        self.assertEqual(len(saida.splitlines()), 2)

    def test_erros(self):
        with self.assertRaises(ValueError):
            csv_para_markdown("")
        with self.assertRaises(ValueError):
            csv_para_markdown("a,b\n1")


if __name__ == "__main__":
    unittest.main()
