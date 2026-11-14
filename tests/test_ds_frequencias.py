import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_frequencias import formatar, moda, tabela_frequencias

DADOS = list("aabbbc")


class TestFrequencias(unittest.TestCase):
    def test_tabela(self):
        t = tabela_frequencias(DADOS)
        self.assertEqual([l.valor for l in t], ["a", "b", "c"])
        self.assertEqual([l.absoluta for l in t], [2, 3, 1])
        self.assertAlmostEqual(t[1].relativa, 0.5)
        self.assertEqual([l.acumulada for l in t], [2, 5, 6])
        self.assertAlmostEqual(t[-1].relativa_acumulada, 1.0)
        self.assertAlmostEqual(t[0].percentual, 100 / 3)

    def test_ordem_frequencia(self):
        t = tabela_frequencias(DADOS, ordem="frequencia")
        self.assertEqual([l.valor for l in t], ["b", "a", "c"])

    def test_moda(self):
        self.assertEqual(moda(DADOS), ["b"])
        self.assertEqual(moda([1, 1, 2, 2, 3]), [1, 2])

    def test_formatar(self):
        txt = formatar(tabela_frequencias(DADOS))
        self.assertEqual(len(txt.splitlines()), 4)
        self.assertIn("50.0", txt.splitlines()[2])

    def test_erros(self):
        with self.assertRaises(ValueError):
            tabela_frequencias([])
        with self.assertRaises(ValueError):
            tabela_frequencias([1], ordem="x")
        with self.assertRaises(ValueError):
            moda([])


if __name__ == "__main__":
    unittest.main()
