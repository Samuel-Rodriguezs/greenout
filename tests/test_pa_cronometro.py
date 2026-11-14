import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_cronometro import Cronometro


def relogio_falso(valores):
    it = iter(valores)
    return lambda: next(it)


class TestCronometro(unittest.TestCase):
    def test_context_manager(self):
        c = Cronometro(relogio_falso([10.0, 12.5]))
        with c:
            pass
        self.assertEqual(c.decorrido, 2.5)

    def test_decorador(self):
        c = Cronometro(relogio_falso([0, 3]))

        @c
        def dobro(x):
            return x * 2

        self.assertEqual(dobro(4), 8)
        self.assertEqual(c.decorrido, 3)
        self.assertEqual(dobro.__name__, "dobro")

    def test_excecao_propagada_e_tempo_registrado(self):
        c = Cronometro(relogio_falso([1, 4]))
        with self.assertRaises(KeyError):
            with c:
                raise KeyError("a")
        self.assertEqual(c.decorrido, 3)

    def test_decorrido_inicial_none(self):
        self.assertIsNone(Cronometro().decorrido)

    def test_relogio_real_nao_negativo(self):
        with Cronometro() as c:
            pass
        self.assertGreaterEqual(c.decorrido, 0)


if __name__ == "__main__":
    unittest.main()
