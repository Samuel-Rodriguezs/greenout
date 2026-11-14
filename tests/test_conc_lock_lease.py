import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_lock_lease import RecursoProtegido, ServidorLocks


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestLockLease(unittest.TestCase):
    def setUp(self):
        self.r = Relogio()
        self.s = ServidorLocks(self.r)

    def test_exclusao_mutua(self):
        self.assertIsNotNone(self.s.adquirir("x", "A", 10))
        self.assertIsNone(self.s.adquirir("x", "B", 10))
        self.assertEqual(self.s.dono_de("x"), "A")

    def test_expiracao_permite_outro_dono(self):
        a = self.s.adquirir("x", "A", 10)
        self.r.t = 10
        b = self.s.adquirir("x", "B", 10)
        self.assertEqual(b.dono, "B")
        self.assertGreater(b.token, a.token)

    def test_renovacao(self):
        a = self.s.adquirir("x", "A", 10)
        self.r.t = 9
        a2 = self.s.renovar(a, 10)
        self.assertEqual(a2.expira_em, 19)
        self.r.t = 15
        self.assertIsNone(self.s.adquirir("x", "B", 5))

    def test_renovar_expirada_falha(self):
        a = self.s.adquirir("x", "A", 5)
        self.r.t = 6
        self.assertIsNone(self.s.renovar(a, 5))

    def test_liberar(self):
        a = self.s.adquirir("x", "A", 5)
        self.assertTrue(self.s.liberar(a))
        self.assertFalse(self.s.liberar(a))
        self.assertIsNotNone(self.s.adquirir("x", "B", 5))

    def test_liberar_concessao_velha_nao_afeta_novo_dono(self):
        a = self.s.adquirir("x", "A", 5)
        self.r.t = 5
        b = self.s.adquirir("x", "B", 5)
        self.assertFalse(self.s.liberar(a))
        self.assertEqual(self.s.dono_de("x"), "B")
        self.assertTrue(self.s.liberar(b))

    def test_reentrada_mantem_token(self):
        a = self.s.adquirir("x", "A", 5)
        a2 = self.s.adquirir("x", "A", 5)
        self.assertEqual(a.token, a2.token)

    def test_recursos_independentes(self):
        self.assertIsNotNone(self.s.adquirir("x", "A", 5))
        self.assertIsNotNone(self.s.adquirir("y", "B", 5))

    def test_fencing_token_bloqueia_cliente_atrasado(self):
        rec = RecursoProtegido()
        a = self.s.adquirir("x", "A", 5)
        self.r.t = 6  # A pausou (GC) e perdeu o lease
        b = self.s.adquirir("x", "B", 5)
        self.assertTrue(rec.escrever(b.token, "B"))
        self.assertFalse(rec.escrever(a.token, "A"))  # A acorda tarde
        self.assertEqual(rec.valor, "B")

    def test_lease_invalido(self):
        with self.assertRaises(ValueError):
            self.s.adquirir("x", "A", 0)


if __name__ == "__main__":
    unittest.main()
