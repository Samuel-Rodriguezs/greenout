import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import ds_deduplicacao as d

REGS = [
    {"id": 1, "nome": "Maria Silva", "cidade": "SP"},
    {"id": 2, "nome": "maria  silva ", "cidade": "sp"},
    {"id": 3, "nome": "MARÍA SILVA", "cidade": "RJ"},
    {"id": 4, "nome": "Ana Souza", "cidade": "SP"},
]


class TestDeduplicacao(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(d.normalizar("  JOÃO   da  Silva "), "joao da silva")
        self.assertEqual(d.normalizar(None), "")
        self.assertEqual(d.normalizar(12), "12")

    def test_primeiro_e_ultimo(self):
        r = d.deduplicar(REGS, ["nome"])
        self.assertEqual([x["id"] for x in r], [1, 4])
        r = d.deduplicar(REGS, ["nome"], manter="ultimo")
        self.assertEqual([x["id"] for x in r], [3, 4])

    def test_chaves_compostas(self):
        r = d.deduplicar(REGS, ["nome", "cidade"])
        self.assertEqual([x["id"] for x in r], [1, 3, 4])

    def test_sem_normalizar(self):
        r = d.deduplicar(REGS, ["nome"], normalizar_chaves=False)
        self.assertEqual(len(r), 4)

    def test_grupos_duplicados(self):
        self.assertEqual(d.grupos_duplicados(REGS, ["nome"]), [[0, 1, 2]])

    def test_similaridade(self):
        self.assertAlmostEqual(d.similaridade("Joao Pereira", "Joao Perreira"), 24 / 25)
        self.assertEqual(d.similaridade("ABC", "abc"), 1.0)

    def test_agrupar_similares(self):
        nomes = ["Joao Pereira", "Ana Souza", "Joao Perreira", "ana souza"]
        self.assertEqual(d.agrupar_similares(nomes, 0.9), [[0, 2], [1, 3]])
        self.assertEqual(d.agrupar_similares(nomes, 1.0), [[0], [1, 3], [2]])

    def test_deduplicar_fuzzy(self):
        regs = [{"n": "Joao Pereira"}, {"n": "Joao Perreira"}, {"n": "Carlos"}]
        self.assertEqual(d.deduplicar_fuzzy(regs, "n", 0.9), [regs[0], regs[2]])

    def test_erros(self):
        with self.assertRaises(ValueError):
            d.deduplicar(REGS, [])
        with self.assertRaises(ValueError):
            d.deduplicar(REGS, ["nome"], manter="x")
        with self.assertRaises(ValueError):
            d.agrupar_similares(["a"], 2)


if __name__ == "__main__":
    unittest.main()
