import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_null_object import LoggerMemoria, LoggerNulo, ProcessadorLote


class TestNullObject(unittest.TestCase):
    def test_sem_logger_funciona(self):
        p = ProcessadorLote()
        self.assertIsInstance(p.logger, LoggerNulo)
        self.assertEqual(p.processar(["a", "", "b"]), 2)

    def test_com_logger(self):
        log = LoggerMemoria()
        ProcessadorLote(log).processar(["a", " "])
        self.assertEqual(log.linhas, ["INFO processado a", "ERRO item vazio"])

    def test_nulo_retorna_none(self):
        self.assertIsNone(LoggerNulo().info("x"))
        self.assertIsNone(LoggerNulo().erro("x"))


if __name__ == "__main__":
    unittest.main()
