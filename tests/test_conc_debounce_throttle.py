import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_debounce_throttle import Debounce, Throttle


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class TestDebounce(unittest.TestCase):
    def test_so_executa_apos_silencio(self):
        r, log = Relogio(), []
        d = Debounce(log.append, 1.0, r)
        d("a")
        r.t = 0.5
        d("b")  # reinicia o prazo
        r.t = 1.2
        self.assertFalse(d.verificar())
        r.t = 1.5
        self.assertTrue(d.verificar())
        self.assertEqual(log, ["b"])
        self.assertFalse(d.pendente)

    def test_nao_executa_duas_vezes(self):
        r, log = Relogio(), []
        d = Debounce(log.append, 1, r)
        d(1)
        r.t = 2
        d.verificar()
        d.verificar()
        self.assertEqual(log, [1])

    def test_cancelar_e_descarregar(self):
        r, log = Relogio(), []
        d = Debounce(log.append, 10, r)
        d("x")
        d.cancelar()
        self.assertFalse(d.descarregar())
        d("y")
        self.assertTrue(d.descarregar())
        self.assertEqual(log, ["y"])

    def test_kwargs(self):
        r, log = Relogio(), []
        d = Debounce(lambda a, b=0: log.append((a, b)), 0, r)
        d(1, b=2)
        self.assertTrue(d.verificar())
        self.assertEqual(log, [(1, 2)])

    def test_invalido(self):
        with self.assertRaises(ValueError):
            Debounce(print, -1)


class TestThrottle(unittest.TestCase):
    def test_limita_frequencia(self):
        r, log = Relogio(), []
        t = Throttle(log.append, 1.0, relogio=r)
        resultados = []
        for i, instante in enumerate([0, 0.2, 0.9, 1.0, 1.5, 2.1]):
            r.t = instante
            resultados.append(t(i))
        self.assertEqual(resultados, [True, False, False, True, False, True])
        self.assertEqual(log, [0, 3, 5])

    def test_trailing(self):
        r, log = Relogio(), []
        t = Throttle(log.append, 1.0, final=True, relogio=r)
        t("a")
        r.t = 0.3
        t("b")
        r.t = 0.6
        t("c")
        self.assertFalse(t.verificar())
        r.t = 1.0
        self.assertTrue(t.verificar())
        self.assertEqual(log, ["a", "c"])
        self.assertFalse(t.verificar())

    def test_sem_trailing_descarta(self):
        r, log = Relogio(), []
        t = Throttle(log.append, 1.0, relogio=r)
        t("a")
        t("b")
        r.t = 5
        self.assertFalse(t.verificar())
        self.assertEqual(log, ["a"])

    def test_invalido(self):
        with self.assertRaises(ValueError):
            Throttle(print, -1)


if __name__ == "__main__":
    unittest.main()
