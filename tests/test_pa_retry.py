import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_retry import retry


class TestRetry(unittest.TestCase):
    def test_sucesso_apos_falhas_com_backoff(self):
        esperas = []
        estado = {"n": 0}

        @retry(tentativas=4, atraso=1, fator=2, dormir=esperas.append)
        def f():
            estado["n"] += 1
            if estado["n"] < 3:
                raise ValueError("x")
            return "ok"

        self.assertEqual(f(), "ok")
        self.assertEqual(esperas, [1, 2])

    def test_esgota_e_propaga(self):
        esperas = []

        @retry(tentativas=3, dormir=esperas.append)
        def f():
            raise RuntimeError("falha")

        with self.assertRaises(RuntimeError):
            f()
        self.assertEqual(len(esperas), 2)

    def test_excecao_nao_listada_nao_repete(self):
        chamadas = []

        @retry(tentativas=5, excecoes=(KeyError,), dormir=lambda s: None)
        def f():
            chamadas.append(1)
            raise ValueError()

        with self.assertRaises(ValueError):
            f()
        self.assertEqual(len(chamadas), 1)

    def test_tentativas_invalidas(self):
        with self.assertRaises(ValueError):
            retry(tentativas=0)

    def test_argumentos_repassados(self):
        @retry(dormir=lambda s: None)
        def soma(a, b=0):
            return a + b

        self.assertEqual(soma(1, b=2), 3)


if __name__ == "__main__":
    unittest.main()
