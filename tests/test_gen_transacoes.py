import dataclasses
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_transacoes as g

INI = datetime(2025, 1, 1)


class TestGenTransacoes(unittest.TestCase):
    def test_determinismo(self):
        self.assertEqual(g.gerar_extrato(1, 100, INI), g.gerar_extrato(1, 100, INI))

    def test_saldo_coerente_em_varias_seeds(self):
        for seed in range(30):
            ext = g.gerar_extrato(seed, 200, INI, saldo_inicial=5000)
            self.assertTrue(g.conferir_extrato(ext, 5000), seed)

    def test_saldo_zero_inicial(self):
        ext = g.gerar_extrato(7, 300, INI, saldo_inicial=0)
        self.assertTrue(g.conferir_extrato(ext, 0))
        self.assertTrue(all(t.saldo_apos >= 0 for t in ext))

    def test_cronologia_e_sequencia(self):
        ext = g.gerar_extrato(2, 100, INI)
        self.assertEqual([t.sequencia for t in ext], list(range(1, 101)))
        self.assertTrue(all(a.quando < b.quando for a, b in zip(ext, ext[1:])))
        self.assertTrue(all(t.valor > 0 and t.tipo in g.TIPOS for t in ext))

    def test_conferencia_detecta_adulteracao(self):
        ext = g.gerar_extrato(3, 50, INI)
        ext[10] = dataclasses.replace(ext[10], saldo_apos=ext[10].saldo_apos + 1)
        self.assertFalse(g.conferir_extrato(ext, 100_000))
        self.assertFalse(g.conferir_extrato(g.gerar_extrato(3, 50, INI), 99_999))

    def test_saldo_inicial_negativo(self):
        with self.assertRaises(ValueError):
            g.gerar_extrato(1, 1, INI, saldo_inicial=-1)

    def test_delta_por_tipo(self):
        ext = g.gerar_extrato(4, 200, INI)
        for t in ext:
            self.assertEqual(t.delta > 0, t.tipo in g.CREDITOS)


if __name__ == "__main__":
    unittest.main()
