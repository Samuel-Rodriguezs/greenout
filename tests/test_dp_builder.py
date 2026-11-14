import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_builder import ConsultaBuilder


class TestBuilder(unittest.TestCase):
    def test_minima(self):
        self.assertEqual(ConsultaBuilder("users").construir().sql,
                         "SELECT * FROM users")

    def test_completa(self):
        q = (ConsultaBuilder("users").colunas("id", "nome")
             .onde("idade > ?", 18).onde("ativo = ?", 1)
             .ordenar("nome", desc=True).limitar(10).construir())
        self.assertEqual(q.sql, "SELECT id, nome FROM users WHERE idade > ? "
                                "AND ativo = ? ORDER BY nome DESC LIMIT 10")
        self.assertEqual(q.params, (18, 1))

    def test_limite_invalido(self):
        with self.assertRaises(ValueError):
            ConsultaBuilder("t").limitar(-1)


if __name__ == "__main__":
    unittest.main()
