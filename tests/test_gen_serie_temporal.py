import random
import statistics
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_serie_temporal as g


class TestGenSerieTemporal(unittest.TestCase):
    def test_determinismo(self):
        p = g.ParametrosSerie()
        self.assertEqual(g.gerar_serie(random.Random(1), p, 50), g.gerar_serie(random.Random(1), p, 50))

    def test_sem_ruido_e_soma_dos_componentes(self):
        p = g.ParametrosSerie(ruido=0.0)
        s = g.gerar_serie(random.Random(0), p, 30)
        tend, saz = g.componentes(p, 30)
        for a, b, c in zip(s, tend, saz):
            self.assertAlmostEqual(a, b + c)

    def test_periodicidade_sem_tendencia(self):
        p = g.ParametrosSerie(tendencia=0.0, ruido=0.0, periodo=12)
        s = g.gerar_serie(random.Random(0), p, 60)
        for t in range(48):
            self.assertAlmostEqual(s[t], s[t + 12])

    def test_ruido_tem_desvio_esperado(self):
        p = g.ParametrosSerie(tendencia=0.0, amplitude=0.0, ruido=3.0)
        s = g.gerar_serie(random.Random(5), p, 20000)
        self.assertAlmostEqual(statistics.mean(s), 100.0, delta=0.15)
        self.assertAlmostEqual(statistics.stdev(s), 3.0, delta=0.1)

    def test_tendencia_recuperada_pela_media_movel(self):
        p = g.ParametrosSerie(tendencia=2.0, amplitude=10.0, periodo=7, ruido=1.0)
        s = g.gerar_serie(random.Random(6), p, 200)
        mm = g.media_movel(s, 7)  # janela = período cancela a sazonalidade
        inclinacao = (mm[-1] - mm[0]) / (len(mm) - 1)
        self.assertAlmostEqual(inclinacao, 2.0, delta=0.1)

    def test_datada(self):
        d = g.gerar_serie_datada(random.Random(1), g.ParametrosSerie(), date(2024, 1, 30), 5)
        self.assertEqual([x for x, _ in d], [date(2024, 1, 30) + timedelta(days=i) for i in range(5)])

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            g.gerar_serie(random.Random(0), g.ParametrosSerie(periodo=0), 5)
        with self.assertRaises(ValueError):
            g.gerar_serie(random.Random(0), g.ParametrosSerie(ruido=-1), 5)
        with self.assertRaises(ValueError):
            g.media_movel([1.0, 2.0], 3)

    def test_media_movel_valores(self):
        self.assertEqual(g.media_movel([1, 2, 3, 4], 2), [1.5, 2.5, 3.5])


if __name__ == "__main__":
    unittest.main()
