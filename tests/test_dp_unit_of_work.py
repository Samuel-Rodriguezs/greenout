import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_unit_of_work import Banco, UnidadeDeTrabalho


class TestUnitOfWork(unittest.TestCase):
    def setUp(self):
        self.banco = Banco({"a": 100, "b": 50, "c": 0})

    def test_commit(self):
        with UnidadeDeTrabalho(self.banco) as uow:
            uow.transferir("a", "b", 30)
            uow.transferir("b", "c", 80)
        self.assertEqual(self.banco.saldos, {"a": 70, "b": 0, "c": 80})

    def test_nada_visivel_antes_do_commit(self):
        with UnidadeDeTrabalho(self.banco) as uow:
            uow.transferir("a", "b", 10)
            self.assertEqual(self.banco.saldos["a"], 100)
            self.assertEqual(uow.saldo("a"), 90)

    def test_rollback_em_erro(self):
        with self.assertRaises(ValueError):
            with UnidadeDeTrabalho(self.banco) as uow:
                uow.transferir("a", "b", 60)
                uow.transferir("c", "a", 1)
        self.assertEqual(self.banco.saldos, {"a": 100, "b": 50, "c": 0})

    def test_valor_invalido(self):
        with self.assertRaises(ValueError):
            with UnidadeDeTrabalho(self.banco) as uow:
                uow.transferir("a", "b", 0)


if __name__ == "__main__":
    unittest.main()
