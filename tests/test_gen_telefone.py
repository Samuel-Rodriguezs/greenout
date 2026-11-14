import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_telefone as g


class TestGenTelefone(unittest.TestCase):
    def test_propriedades(self):
        for t in g.gerar_lote(random.Random(4), 500):
            self.assertTrue(g.eh_celular_valido(t))
            self.assertEqual(t[2], "9")

    def test_determinismo(self):
        self.assertEqual(g.gerar_lote(random.Random(1), 50), g.gerar_lote(random.Random(1), 50))

    def test_ddd_fixo_e_invalido(self):
        self.assertTrue(g.gerar_celular(random.Random(0), 85).startswith("85"))
        with self.assertRaises(ValueError):
            g.gerar_celular(random.Random(0), 10)

    def test_formatacao(self):
        self.assertEqual(g.formatar_celular("11987654321"), "(11) 98765-4321")
        with self.assertRaises(ValueError):
            g.formatar_celular("123")

    def test_unicos(self):
        lote = g.gerar_lote(random.Random(2), 1000)
        self.assertEqual(len(set(lote)), 1000)

    def test_validador_rejeita(self):
        self.assertFalse(g.eh_celular_valido("11887654321"))
        self.assertFalse(g.eh_celular_valido("10987654321"))


if __name__ == "__main__":
    unittest.main()
