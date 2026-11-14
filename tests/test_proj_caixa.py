import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_caixa import CaixaEletronico, ErroCaixa


class TestCaixa(unittest.TestCase):
    def setUp(self):
        self.c = CaixaEletronico("1234", 500, limite_diario=300)
        self.c.autenticar("1234")

    def test_saque_cedulas(self):
        self.assertEqual(self.c.sacar(180), {100: 1, 50: 1, 20: 1, 10: 1})
        self.assertEqual(self.c.saldo, 320)

    def test_deposito_e_extrato(self):
        self.c.depositar(100)
        self.c.sacar(50)
        self.assertEqual(self.c.saldo, 550)
        self.assertEqual(self.c.extrato, ["deposito 100", "saque 50"])

    def test_limite_diario(self):
        self.c.sacar(200)
        with self.assertRaises(ErroCaixa):
            self.c.sacar(200)

    def test_saldo_insuficiente(self):
        c = CaixaEletronico("1", 50)
        c.autenticar("1")
        with self.assertRaises(ErroCaixa):
            c.sacar(100)

    def test_valores_invalidos(self):
        for v in (0, -10, 15):
            with self.assertRaises(ErroCaixa):
                self.c.sacar(v)
        with self.assertRaises(ErroCaixa):
            self.c.depositar(0)

    def test_exige_login(self):
        self.c.sair()
        with self.assertRaises(ErroCaixa):
            self.c.sacar(10)

    def test_bloqueio_apos_tres_erros(self):
        c = CaixaEletronico("1234", 100)
        self.assertFalse(c.autenticar("0"))
        self.assertFalse(c.autenticar("0"))
        self.assertFalse(c.autenticar("0"))
        with self.assertRaises(ErroCaixa):
            c.autenticar("1234")


if __name__ == "__main__":
    unittest.main()
