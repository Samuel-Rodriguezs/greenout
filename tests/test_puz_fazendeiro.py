import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_fazendeiro import (FINAL, INICIAL, contar_estados_alcancaveis,
                            resolver, seguro, sucessores)


class TestFazendeiro(unittest.TestCase):
    def test_solucao_tem_sete_travessias(self):
        sol = resolver()
        self.assertEqual(len(sol), 7)
        self.assertEqual(sol[0], "cabra")
        self.assertEqual(sol[-1], "cabra")

    def test_solucao_e_valida(self):
        estado = INICIAL
        for carga in resolver():
            proximos = dict(sucessores(estado))
            self.assertIn(carga, proximos)
            estado = proximos[carga]
            self.assertTrue(seguro(estado))
        self.assertEqual(estado, FINAL)

    def test_estados_inseguros(self):
        self.assertFalse(seguro((1, 0, 0, 1)))  # lobo e cabra sozinhos
        self.assertFalse(seguro((1, 1, 0, 0)))  # cabra e couve sozinhas
        self.assertTrue(seguro((1, 0, 1, 0)))

    def test_estado_inicial_inseguro_sem_solucao(self):
        self.assertIsNone(resolver((1, 0, 0, 1)))

    def test_ja_resolvido(self):
        self.assertEqual(resolver(FINAL), [])

    def test_espaco_de_estados(self):
        self.assertEqual(contar_estados_alcancaveis(), 10)


if __name__ == "__main__":
    unittest.main()
