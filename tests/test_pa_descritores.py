import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_descritores import Campo, Ponto


class TestDescritores(unittest.TestCase):
    def test_valores_validos(self):
        p = Ponto(1, 2.5)
        self.assertEqual((p.x, p.y), (1, 2.5))
        p.x = 10
        self.assertEqual(p.x, 10)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            Ponto("a", 1)
        with self.assertRaises(ValueError):
            Ponto(True, 1)
        p = Ponto(0, 0)
        with self.assertRaises(ValueError):
            p.y = None
        self.assertEqual(p.y, 0)

    def test_slots_impede_atributos_novos(self):
        with self.assertRaises(AttributeError):
            Ponto(0, 0).z = 1
        self.assertFalse(hasattr(Ponto(0, 0), "__dict__"))

    def test_acesso_na_classe_retorna_descritor(self):
        self.assertIsInstance(Ponto.x, Campo)

    def test_repr(self):
        self.assertEqual(repr(Ponto(1, 2)), "Ponto(1, 2)")

    def test_campo_em_classe_comum_e_nao_inicializado(self):
        class C:
            idade = Campo(lambda v: v >= 0, "negativa")

        c = C()
        with self.assertRaises(AttributeError):
            c.idade
        with self.assertRaises(ValueError):
            c.idade = -1
        c.idade = 3
        self.assertEqual(c.idade, 3)


if __name__ == "__main__":
    unittest.main()
