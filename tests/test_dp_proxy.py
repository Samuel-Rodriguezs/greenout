import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_proxy import ArmazenamentoLento, ProxyArmazenamento

DADOS = {"a": "publico", "s": "segredo"}


class TestProxy(unittest.TestCase):
    def test_cache(self):
        real = ArmazenamentoLento(DADOS)
        p = ProxyArmazenamento(real, "ana")
        self.assertEqual(p.ler("a"), "publico")
        p.ler("a")
        self.assertEqual(real.leituras, 1)

    def test_acesso_negado(self):
        real = ArmazenamentoLento(DADOS)
        p = ProxyArmazenamento(real, "ana", {"s"})
        with self.assertRaises(PermissionError):
            p.ler("s")
        self.assertEqual(real.leituras, 0)

    def test_admin(self):
        p = ProxyArmazenamento(ArmazenamentoLento(DADOS), "admin", {"s"})
        self.assertEqual(p.ler("s"), "segredo")

    def test_erro_propaga(self):
        with self.assertRaises(KeyError):
            ProxyArmazenamento(ArmazenamentoLento(DADOS), "x").ler("z")


if __name__ == "__main__":
    unittest.main()
