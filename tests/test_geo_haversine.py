import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from geo_haversine import RAIO_TERRA_KM, destino, distancia_km, ponto_medio, rumo_inicial

SAO_PAULO = (-23.5505, -46.6333)
RIO = (-22.9068, -43.1729)
LONDRES = (51.5074, -0.1278)
PARIS = (48.8566, 2.3522)


class TestHaversine(unittest.TestCase):
    def test_distancias_conhecidas(self):
        self.assertAlmostEqual(distancia_km(LONDRES, PARIS), 343.5, delta=1.5)
        self.assertAlmostEqual(distancia_km(SAO_PAULO, RIO), 360.7, delta=2)

    def test_zero_e_simetria(self):
        self.assertEqual(distancia_km(RIO, RIO), 0)
        self.assertAlmostEqual(distancia_km(RIO, PARIS), distancia_km(PARIS, RIO))

    def test_um_grau_no_equador(self):
        self.assertAlmostEqual(distancia_km((0, 0), (0, 1)), RAIO_TERRA_KM * math.pi / 180)

    def test_antipodas_e_polos(self):
        self.assertAlmostEqual(distancia_km((0, 0), (0, 180)), RAIO_TERRA_KM * math.pi)
        self.assertAlmostEqual(distancia_km((90, 0), (-90, 0)), RAIO_TERRA_KM * math.pi)

    def test_travessia_antimeridiano(self):
        self.assertAlmostEqual(distancia_km((0, 179.5), (0, -179.5)), RAIO_TERRA_KM * math.pi / 180)

    def test_coordenada_invalida(self):
        with self.assertRaises(ValueError):
            distancia_km((91, 0), (0, 0))
        with self.assertRaises(ValueError):
            rumo_inicial((0, 0), (0, 181))

    def test_rumos_cardeais(self):
        self.assertAlmostEqual(rumo_inicial((0, 0), (10, 0)), 0)
        self.assertAlmostEqual(rumo_inicial((0, 0), (0, 10)), 90)
        self.assertAlmostEqual(rumo_inicial((0, 0), (-10, 0)), 180)
        self.assertAlmostEqual(rumo_inicial((0, 0), (0, -10)), 270)

    def test_rumo_londres_paris(self):
        self.assertAlmostEqual(rumo_inicial(LONDRES, PARIS), 148.1, delta=0.5)

    def test_destino_ida_e_volta(self):
        d = distancia_km(LONDRES, PARIS)
        lat, lon = destino(LONDRES, rumo_inicial(LONDRES, PARIS), d)
        self.assertAlmostEqual(lat, PARIS[0], places=4)
        self.assertAlmostEqual(lon, PARIS[1], places=4)

    def test_destino_norte(self):
        lat, lon = destino((0, 10), 0, RAIO_TERRA_KM * math.pi / 180 * 5)
        self.assertAlmostEqual(lat, 5)
        self.assertAlmostEqual(lon, 10)

    def test_ponto_medio(self):
        lat, lon = ponto_medio((0, 0), (0, 90))
        self.assertAlmostEqual(lat, 0)
        self.assertAlmostEqual(lon, 45)
        m = ponto_medio(LONDRES, PARIS)
        self.assertAlmostEqual(distancia_km(LONDRES, m), distancia_km(m, PARIS))


if __name__ == "__main__":
    unittest.main()
