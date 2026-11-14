import random
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_lorem as g

VOCAB = set(g.PALAVRAS + g.ADJETIVOS + g.VERBOS + g.CONECTIVOS)


class TestGenLorem(unittest.TestCase):
    def test_determinismo(self):
        self.assertEqual(g.gerar_texto(1, 5), g.gerar_texto(1, 5))
        self.assertNotEqual(g.gerar_texto(1, 5), g.gerar_texto(2, 5))

    def test_frase_forma(self):
        rng = random.Random(3)
        for _ in range(300):
            f = g.gerar_frase(rng, 6, 14)
            self.assertTrue(f[0].isupper())
            self.assertTrue(f.endswith(".") and not f.endswith(" ."))
            palavras = re.findall(r"[^\s,.]+", f.lower())
            self.assertTrue(set(palavras) <= VOCAB)
            self.assertLessEqual(len(palavras), 14)
            self.assertGreaterEqual(len(palavras), 2)
            self.assertNotIn(palavras[-1], g.CONECTIVOS)

    def test_paragrafos(self):
        t = g.gerar_texto(4, 4)
        self.assertEqual(len(t.split("\n\n")), 4)
        for p in t.split("\n\n"):
            self.assertTrue(3 <= p.count(". ") + 1 <= 6)

    def test_sem_espacos_duplos_nem_virgula_dupla(self):
        t = g.gerar_texto(5, 10)
        self.assertNotIn("  ", t)
        self.assertNotIn(",,", t)
        self.assertNotIn(" ,", t)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            g.gerar_frase(random.Random(0), 1, 5)
        with self.assertRaises(ValueError):
            g.gerar_paragrafo(random.Random(0), 0)

    def test_palavras(self):
        w = g.gerar_palavras(random.Random(6), 40)
        self.assertEqual(len(w), 40)
        self.assertTrue(set(w) <= VOCAB)


if __name__ == "__main__":
    unittest.main()
