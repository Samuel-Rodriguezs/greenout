import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_documentos as g
from dt_cnpj import validar_cnpj
from util_cpf import validar_cpf


class TestGenDocumentos(unittest.TestCase):
    def test_cpf_valido_por_validador_independente(self):
        rng = random.Random(42)
        for _ in range(500):
            self.assertTrue(validar_cpf(g.gerar_cpf(rng)))
            self.assertTrue(validar_cpf(g.gerar_cpf(rng, formatado=True)))

    def test_cnpj_valido_por_validador_independente(self):
        rng = random.Random(42)
        for _ in range(500):
            self.assertTrue(validar_cnpj(g.gerar_cnpj(rng)))
            self.assertTrue(validar_cnpj(g.gerar_cnpj(rng, formatado=True)))

    def test_formatos(self):
        rng = random.Random(1)
        self.assertRegex(g.gerar_cpf(rng, True), r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
        self.assertRegex(g.gerar_cnpj(rng, True), r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")
        self.assertEqual(len(g.gerar_cpf(rng)), 11)
        self.assertEqual(len(g.gerar_cnpj(rng)), 14)

    def test_filial(self):
        c = g.gerar_cnpj(random.Random(3), filial=27)
        self.assertEqual(c[8:12], "0027")
        self.assertTrue(validar_cnpj(c))
        with self.assertRaises(ValueError):
            g.gerar_cnpj(random.Random(3), filial=0)

    def test_matriz_por_padrao(self):
        self.assertEqual(g.gerar_cnpj(random.Random(3))[8:12], "0001")

    def test_determinismo(self):
        self.assertEqual(g.gerar_cpf(random.Random(5)), g.gerar_cpf(random.Random(5)))
        self.assertEqual(g.gerar_cnpj(random.Random(5)), g.gerar_cnpj(random.Random(5)))

    def test_lote_distinto_e_valido(self):
        lote = g.gerar_lote_cpf(random.Random(8), 400)
        self.assertEqual(len(set(lote)), 400)
        self.assertTrue(all(validar_cpf(c) for c in lote))
        self.assertEqual(lote, g.gerar_lote_cpf(random.Random(8), 400))

    def test_corromper_digito_invalida(self):
        cpf = g.gerar_cpf(random.Random(9))
        errado = cpf[:-1] + str((int(cpf[-1]) + 1) % 10)
        self.assertFalse(validar_cpf(errado))


if __name__ == "__main__":
    unittest.main()
