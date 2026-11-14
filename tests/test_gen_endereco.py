import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_endereco as g
from dt_cep import regiao_postal, validar_cep


class TestGenEndereco(unittest.TestCase):
    def test_cep_valido(self):
        rng = random.Random(1)
        for _ in range(500):
            self.assertTrue(validar_cep(g.gerar_cep(rng)))
            self.assertTrue(validar_cep(g.gerar_cep(rng, formatado=False)))

    def test_cep_regiao(self):
        rng = random.Random(2)
        for r in range(10):
            self.assertEqual(g.gerar_cep(rng, r)[0], str(r))
        with self.assertRaises(ValueError):
            g.gerar_cep(rng, 10)

    def test_cep_nunca_zerado(self):
        rng = random.Random(3)
        self.assertTrue(all(g.gerar_cep(rng, 0) != "00000-000" for _ in range(2000)))

    def test_endereco_coerente_com_regiao(self):
        for e in g.gerar_lote(random.Random(4), 200):
            cidade = next(c for c in g.CIDADES if c[1] == e.cidade and c[0] == e.uf)
            self.assertEqual(int(e.cep[0]), cidade[2])
            self.assertTrue(validar_cep(e.cep))
            self.assertTrue(regiao_postal(e.cep))
            self.assertGreaterEqual(e.numero, 1)

    def test_determinismo(self):
        self.assertEqual(g.gerar_lote(random.Random(6), 20), g.gerar_lote(random.Random(6), 20))

    def test_formatado(self):
        e = g.Endereco("Rua A", 10, "Apto 1", "Centro", "Recife", "PE", "50000-000")
        self.assertEqual(e.formatado(), "Rua A, 10, Apto 1 - Centro, Recife/PE - CEP 50000-000")
        e2 = g.Endereco("Rua A", 10, "", "Centro", "Recife", "PE", "50000-000")
        self.assertNotIn(", ,", e2.formatado())
        self.assertIn("10 - Centro", e2.formatado())


if __name__ == "__main__":
    unittest.main()
