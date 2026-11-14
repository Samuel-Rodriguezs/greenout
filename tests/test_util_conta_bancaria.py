import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_conta_bancaria import ContaBancaria, SaldoInsuficienteError, ValorInvalidoError


class TestContaBancaria(unittest.TestCase):
    def test_deposito_e_saque(self):
        c = ContaBancaria("Ana", 100)
        self.assertEqual(c.depositar(50), 150)
        self.assertEqual(c.sacar(30), 120)
        self.assertEqual(c.extrato, [("deposito", 50.0), ("saque", 30.0)])

    def test_saque_exato_zera(self):
        c = ContaBancaria("Ana", 10)
        self.assertEqual(c.sacar(10), 0)

    def test_saldo_insuficiente(self):
        c = ContaBancaria("Ana", 10)
        with self.assertRaises(SaldoInsuficienteError):
            c.sacar(10.01)
        self.assertEqual(c.saldo, 10)
        self.assertEqual(c.extrato, [])

    def test_valores_invalidos(self):
        c = ContaBancaria("Ana")
        for v in (0, -5, "10", None, True):
            with self.subTest(v=v):
                with self.assertRaises(ValorInvalidoError):
                    c.depositar(v)

    def test_construtor(self):
        with self.assertRaises(ValueError):
            ContaBancaria("  ")
        with self.assertRaises(ValorInvalidoError):
            ContaBancaria("Ana", -1)

    def test_transferencia(self):
        a, b = ContaBancaria("Ana", 100), ContaBancaria("Bia")
        a.transferir(b, 40)
        self.assertEqual((a.saldo, b.saldo), (60, 40))

    def test_transferencia_falha_nao_altera(self):
        a, b = ContaBancaria("Ana", 10), ContaBancaria("Bia")
        with self.assertRaises(SaldoInsuficienteError):
            a.transferir(b, 50)
        self.assertEqual((a.saldo, b.saldo), (10, 0))
        with self.assertRaises(ValueError):
            a.transferir(a, 1)

    def test_extrato_e_copia(self):
        c = ContaBancaria("Ana", 5)
        c.extrato.append(("x", 1))
        self.assertEqual(c.extrato, [])


if __name__ == "__main__":
    unittest.main()
