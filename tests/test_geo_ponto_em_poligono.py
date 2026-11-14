import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_ponto_em_poligono import (
    DENTRO,
    FORA,
    FRONTEIRA,
    classificar,
    ray_casting,
    winding_number,
)

QUADRADO = [(0, 0), (4, 0), (4, 4), (0, 4)]
U = [(0, 0), (6, 0), (6, 4), (4, 4), (4, 2), (2, 2), (2, 4), (0, 4)]
# estrela pentagrama: o centro tem winding 2 mas é "dentro" em ambos
ESTRELA = [(0, 3), (1, -2), (-2, 1), (2, 1), (-1, -2)]


class TestPontoEmPoligono(unittest.TestCase):
    def test_dentro_e_fora(self):
        for f in (ray_casting, classificar):
            self.assertEqual(f((2, 2), QUADRADO), DENTRO)
            self.assertEqual(f((5, 2), QUADRADO), FORA)
            self.assertEqual(f((-1, -1), QUADRADO), FORA)

    def test_fronteira_aresta_e_vertice(self):
        for f in (ray_casting, classificar):
            self.assertEqual(f((2, 0), QUADRADO), FRONTEIRA)
            self.assertEqual(f((4, 4), QUADRADO), FRONTEIRA)
            self.assertEqual(f((0, 2), QUADRADO), FRONTEIRA)

    def test_raio_passa_por_vertice(self):
        # y=4 coincide com vértices do U; ponto na cavidade
        self.assertEqual(ray_casting((3, 3), U), FORA)
        self.assertEqual(classificar((3, 3), U), FORA)
        self.assertEqual(ray_casting((3, 1), U), DENTRO)
        self.assertEqual(ray_casting((1, 4), U), FRONTEIRA)
        self.assertEqual(ray_casting((-1, 4), U), FORA)

    def test_concavo_fora_na_altura_do_vertice(self):
        self.assertEqual(ray_casting((3, 2), U), FRONTEIRA)
        self.assertEqual(ray_casting((7, 2), U), FORA)

    def test_winding_sinal(self):
        self.assertEqual(winding_number((2, 2), QUADRADO), 1)
        self.assertEqual(winding_number((2, 2), QUADRADO[::-1]), -1)
        self.assertEqual(winding_number((9, 9), QUADRADO), 0)

    def test_estrela_regra_par_impar_vs_enrolamento(self):
        self.assertEqual(winding_number((0, 0), ESTRELA), -2)  # sentido horário
        self.assertEqual(ray_casting((0, 0), ESTRELA), FORA)  # par-ímpar
        self.assertEqual(classificar((0, 0), ESTRELA), DENTRO)  # enrolamento

    def test_degenerado(self):
        self.assertEqual(ray_casting((1, 1), []), FORA)
        self.assertEqual(ray_casting((0, 0), [(0, 0), (2, 0)]), FRONTEIRA)
        self.assertEqual(ray_casting((1, 1), [(0, 0), (2, 0)]), FORA)


if __name__ == "__main__":
    unittest.main()
